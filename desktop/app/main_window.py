"""
HSBVectoAI — Main Application Window
Sidebar navigation + content area (Chat / Tools / Settings).
"""

import sys
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QFrame, QStackedWidget, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QIcon

from app.core.config import (
    APP_NAME, APP_DISPLAY_NAME,
    WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT,
    WINDOW_DEFAULT_WIDTH, WINDOW_DEFAULT_HEIGHT,
)
from app.core.auth import AuthManager
from app.core.license import LicenseManager
from app.core.ai_client import AIClient
from app.core.corel_bridge import CorelDRAWBridge
from app.ui.styles import STYLESHEET
from app.ui.login_dialog import LoginDialog
from app.ui.chat_panel import ChatPanel
from app.ui.settings_panel import SettingsPanel


class SessionValidationWorker(QThread):
    result = pyqtSignal(dict)

    def __init__(self, auth):
        super().__init__()
        self._auth = auth

    def run(self):
        self.result.emit(self._auth.validate_session())


class LicenseWorker(QThread):
    result = pyqtSignal(dict)

    def __init__(self, license_mgr):
        super().__init__()
        self._license = license_mgr

    def run(self):
        self.result.emit(self._license.verify())


class MainWindow(QMainWindow):
    """Main application window with sidebar + content pages."""

    def __init__(self):
        super().__init__()
        # Core services
        self._auth = AuthManager()
        self._license = LicenseManager(self._auth)
        self._ai = AIClient(self._auth)
        self._corel = CorelDRAWBridge()

        self._setup_window()
        self._build_ui()
        self._start_session()

        # CorelDRAW status polling every 10s
        self._corel_timer = QTimer(self)
        self._corel_timer.timeout.connect(self._poll_corel_status)
        self._corel_timer.start(10_000)

    # ── Window setup ───────────────────────────────────────────

    def _setup_window(self):
        self.setWindowTitle(APP_DISPLAY_NAME)
        self.setMinimumSize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        self.resize(WINDOW_DEFAULT_WIDTH, WINDOW_DEFAULT_HEIGHT)
        self.setStyleSheet(STYLESHEET)

        # Keep on top option (useful alongside CorelDRAW)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, False)

    # ── UI Build ───────────────────────────────────────────────

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        root = QHBoxLayout(central)
        root.setSpacing(0)
        root.setContentsMargins(0, 0, 0, 0)

        # ── Sidebar ───────────────────────────────────────────
        sidebar = self._build_sidebar()
        root.addWidget(sidebar)

        # Vertical separator
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setStyleSheet("color: #252840;")
        root.addWidget(sep)

        # ── Content area ──────────────────────────────────────
        self._stack = QStackedWidget()
        root.addWidget(self._stack, stretch=1)

        # Pages
        self._chat_panel = ChatPanel(self._ai, self._corel, self)
        self._chat_panel.action_requested.connect(self._on_corel_action)
        self._stack.addWidget(self._chat_panel)          # index 0 = Chat

        self._settings_panel = SettingsPanel(self._auth, self._license, self)
        self._settings_panel.logout_requested.connect(self._logout)
        self._stack.addWidget(self._settings_panel)      # index 1 = Settings

        # Show chat by default
        self._nav_to(0)

    def _build_sidebar(self) -> QWidget:
        sidebar = QWidget()
        sidebar.setFixedWidth(64)
        sidebar.setStyleSheet("background: #14161F;")

        layout = QVBoxLayout(sidebar)
        layout.setSpacing(4)
        layout.setContentsMargins(8, 12, 8, 12)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Logo
        logo = QLabel("⚡")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setFont(QFont("Segoe UI", 22))
        logo.setFixedHeight(48)
        layout.addWidget(logo)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color: #252840; margin: 4px 0;")
        layout.addWidget(sep)

        # Nav buttons
        self._nav_buttons = []

        chat_btn = self._make_nav_btn("💬", "Sohbet", 0)
        layout.addWidget(chat_btn)

        settings_btn = self._make_nav_btn("⚙️", "Ayarlar", 1)
        layout.addWidget(settings_btn)

        layout.addStretch()

        # License status dot at bottom
        self._license_dot = QLabel("●")
        self._license_dot.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._license_dot.setStyleSheet("color: #F59E0B; font-size: 10px;")
        self._license_dot.setToolTip("Lisans kontrol ediliyor…")
        layout.addWidget(self._license_dot)

        return sidebar

    def _make_nav_btn(self, icon: str, tooltip: str, page_idx: int) -> QPushButton:
        btn = QPushButton(icon)
        btn.setToolTip(tooltip)
        btn.setFixedSize(48, 48)
        btn.setFont(QFont("Segoe UI", 18))
        btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                border-radius: 10px;
                color: #6B7280;
                font-size: 20px;
            }
            QPushButton:hover { background: #1C1F2E; color: #E8EAF6; }
            QPushButton[active="true"] { background: #1C2A4A; color: #4F6EF7; }
        """)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(lambda: self._nav_to(page_idx))
        self._nav_buttons.append((btn, page_idx))
        return btn

    def _nav_to(self, page_idx: int):
        self._stack.setCurrentIndex(page_idx)
        for btn, idx in self._nav_buttons:
            btn.setProperty("active", str(idx == page_idx).lower())
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    # ── Session management ────────────────────────────────────

    def _start_session(self):
        """Try to restore saved session, else show login."""
        if self._auth.load_token():
            self._validate_worker = SessionValidationWorker(self._auth)
            self._validate_worker.result.connect(self._on_session_validated)
            self._validate_worker.start()
        else:
            self._show_login()

    def _on_session_validated(self, result: dict):
        if result.get("valid"):
            self._on_login_success(result.get("user", {}))
        else:
            self._show_login()

    def _show_login(self):
        dialog = LoginDialog(self._auth, self)
        dialog.login_success.connect(self._on_login_success)
        if dialog.exec() != dialog.DialogCode.Accepted:
            sys.exit(0)  # User closed dialog without logging in

    def _on_login_success(self, user_data: dict):
        # Verify license in background
        self._license_worker = LicenseWorker(self._license)
        self._license_worker.result.connect(self._on_license_verified)
        self._license_worker.start()

    def _on_license_verified(self, result: dict):
        if result.get("valid"):
            self._license_dot.setStyleSheet("color: #22D3A5; font-size: 10px;")
            self._license_dot.setToolTip(
                f"Aktif — {result.get('plan', '?').capitalize()} Plan"
            )
            self._settings_panel.refresh_license(result)
        else:
            self._license_dot.setStyleSheet("color: #EF4444; font-size: 10px;")
            self._license_dot.setToolTip(result.get("error", "Lisans geçersiz."))

    def _logout(self):
        self._auth.logout()
        self._show_login()

    # ── CorelDRAW ─────────────────────────────────────────────

    def _poll_corel_status(self):
        connected = self._corel.refresh()
        self._chat_panel.update_corel_status(connected)

    def _on_corel_action(self, action: dict):
        """Execute a CorelDRAW action returned by AI."""
        result = self._corel.execute_action(action)
        if not result.get("success"):
            # Show error in chat
            pass  # TODO: feed back to chat panel
