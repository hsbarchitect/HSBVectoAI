"""
Login / Register dialog — shown on first launch or after logout.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFrame, QStackedWidget, QWidget
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont

from app.core.config import APP_NAME, COLOR_ACCENT


class LoginWorker(QThread):
    """Background thread for login to avoid blocking UI."""
    result = pyqtSignal(dict)

    def __init__(self, auth, email, password):
        super().__init__()
        self._auth = auth
        self._email = email
        self._password = password

    def run(self):
        result = self._auth.login(self._email, self._password)
        self.result.emit(result)


class LoginDialog(QDialog):
    """Fullscreen-style login card with email/password."""

    login_success = pyqtSignal(dict)  # emits user data

    def __init__(self, auth_manager, parent=None):
        super().__init__(parent)
        self._auth = auth_manager
        self._worker = None
        self.setWindowTitle(f"{APP_NAME} — Giriş")
        self.setFixedSize(380, 520)
        self.setModal(True)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(36, 40, 36, 40)

        # Logo / title
        logo = QLabel("⚡")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setFont(QFont("Segoe UI", 40))
        layout.addWidget(logo)

        title = QLabel(APP_NAME)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setObjectName("titleLabel")
        layout.addWidget(title)

        sub = QLabel("Smart Design for CorelDRAW")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setObjectName("subtitleLabel")
        layout.addWidget(sub)

        layout.addSpacing(32)

        # Stacked: Login / Register tabs
        self._stack = QStackedWidget()
        self._stack.addWidget(self._build_login_page())
        self._stack.addWidget(self._build_register_page())
        layout.addWidget(self._stack)

    def _build_login_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(12)

        lbl = QLabel("GİRİŞ YAP")
        lbl.setObjectName("sectionLabel")
        layout.addWidget(lbl)

        self._email_input = QLineEdit()
        self._email_input.setPlaceholderText("E-posta adresiniz")
        layout.addWidget(self._email_input)

        self._pass_input = QLineEdit()
        self._pass_input.setPlaceholderText("Şifreniz")
        self._pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self._pass_input)

        self._error_lbl = QLabel()
        self._error_lbl.setStyleSheet("color: #EF4444; font-size: 12px;")
        self._error_lbl.hide()
        layout.addWidget(self._error_lbl)

        self._login_btn = QPushButton("Giriş Yap")
        self._login_btn.setObjectName("primaryBtn")
        self._login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._login_btn.clicked.connect(self._do_login)
        self._pass_input.returnPressed.connect(self._do_login)
        layout.addWidget(self._login_btn)

        # Switch to register
        switch_row = QHBoxLayout()
        switch_row.addWidget(QLabel("Hesabın yok mu?"))
        reg_link = QPushButton("Kayıt Ol")
        reg_link.setObjectName("ghostBtn")
        reg_link.setCursor(Qt.CursorShape.PointingHandCursor)
        reg_link.clicked.connect(lambda: self._stack.setCurrentIndex(1))
        switch_row.addWidget(reg_link)
        switch_row.addStretch()
        layout.addLayout(switch_row)

        # Forgot password
        forgot = QPushButton("Şifremi unuttum")
        forgot.setObjectName("ghostBtn")
        forgot.setCursor(Qt.CursorShape.PointingHandCursor)
        forgot.clicked.connect(self._open_forgot_password)
        layout.addWidget(forgot, alignment=Qt.AlignmentFlag.AlignLeft)

        layout.addStretch()

        # Pricing link
        pricing = QPushButton("💳 Abonelik Planları →")
        pricing.setObjectName("ghostBtn")
        pricing.setCursor(Qt.CursorShape.PointingHandCursor)
        pricing.clicked.connect(self._open_pricing)
        layout.addWidget(pricing, alignment=Qt.AlignmentFlag.AlignCenter)

        return page

    def _build_register_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(12)

        lbl = QLabel("KAYIT OL")
        lbl.setObjectName("sectionLabel")
        layout.addWidget(lbl)

        self._reg_name = QLineEdit()
        self._reg_name.setPlaceholderText("Ad Soyad")
        layout.addWidget(self._reg_name)

        self._reg_email = QLineEdit()
        self._reg_email.setPlaceholderText("E-posta adresiniz")
        layout.addWidget(self._reg_email)

        self._reg_pass = QLineEdit()
        self._reg_pass.setPlaceholderText("Şifre (min. 8 karakter)")
        self._reg_pass.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self._reg_pass)

        self._reg_error = QLabel()
        self._reg_error.setStyleSheet("color: #EF4444; font-size: 12px;")
        self._reg_error.hide()
        layout.addWidget(self._reg_error)

        register_btn = QPushButton("Ücretsiz Dene (7 Gün)")
        register_btn.setObjectName("primaryBtn")
        register_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        register_btn.clicked.connect(self._do_register)
        layout.addWidget(register_btn)

        back_row = QHBoxLayout()
        back_row.addWidget(QLabel("Zaten hesabın var mı?"))
        back = QPushButton("Giriş Yap")
        back.setObjectName("ghostBtn")
        back.setCursor(Qt.CursorShape.PointingHandCursor)
        back.clicked.connect(lambda: self._stack.setCurrentIndex(0))
        back_row.addWidget(back)
        back_row.addStretch()
        layout.addLayout(back_row)
        layout.addStretch()

        return page

    # ── Actions ───────────────────────────────────────────────

    def _do_login(self):
        email = self._email_input.text().strip()
        password = self._pass_input.text()
        if not email or not password:
            self._show_error("E-posta ve şifre gerekli.")
            return

        self._login_btn.setEnabled(False)
        self._login_btn.setText("Giriş yapılıyor…")
        self._error_lbl.hide()

        self._worker = LoginWorker(self._auth, email, password)
        self._worker.result.connect(self._on_login_result)
        self._worker.start()

    def _on_login_result(self, result: dict):
        self._login_btn.setEnabled(True)
        self._login_btn.setText("Giriş Yap")
        if result["success"]:
            self.login_success.emit(result["user"])
            self.accept()
        else:
            self._show_error(result.get("error", "Giriş başarısız."))

    def _do_register(self):
        import webbrowser
        webbrowser.open("https://hsbvectoai.com/register")

    def _open_forgot_password(self):
        import webbrowser
        webbrowser.open("https://hsbvectoai.com/forgot-password")

    def _open_pricing(self):
        import webbrowser
        webbrowser.open("https://hsbvectoai.com/pricing")

    def _show_error(self, msg: str):
        self._error_lbl.setText(msg)
        self._error_lbl.show()
