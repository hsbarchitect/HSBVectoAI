"""
Settings panel — account info, subscription, model preferences.
"""

import webbrowser
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QGroupBox, QFrame, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal

from app.core.config import APP_VERSION, APP_NAME, PLANS


class SettingsPanel(QWidget):
    """User account + subscription info + preferences."""

    logout_requested = pyqtSignal()
    upgrade_requested = pyqtSignal()

    def __init__(self, auth_manager, license_manager, parent=None):
        super().__init__(parent)
        self._auth = auth_manager
        self._license = license_manager
        self._build_ui()

    def _build_ui(self):
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)

        # ── Account section ───────────────────────────────────
        account_box = QGroupBox("Hesap Bilgileri")
        acc_layout = QVBoxLayout(account_box)

        self._email_lbl = QLabel(self._auth.email or "—")
        self._email_lbl.setObjectName("subtitleLabel")
        acc_layout.addWidget(self._email_lbl)

        logout_btn = QPushButton("🚪 Çıkış Yap")
        logout_btn.setObjectName("dangerBtn")
        logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        logout_btn.clicked.connect(self.logout_requested.emit)
        acc_layout.addWidget(logout_btn)

        layout.addWidget(account_box)

        # ── Subscription section ──────────────────────────────
        sub_box = QGroupBox("Abonelik")
        sub_layout = QVBoxLayout(sub_box)

        self._plan_lbl = QLabel("Plan yükleniyor…")
        self._plan_lbl.setObjectName("titleLabel")
        sub_layout.addWidget(self._plan_lbl)

        self._status_lbl = QLabel()
        self._status_lbl.setObjectName("subtitleLabel")
        sub_layout.addWidget(self._status_lbl)

        self._messages_lbl = QLabel()
        self._messages_lbl.setObjectName("subtitleLabel")
        sub_layout.addWidget(self._messages_lbl)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sub_layout.addWidget(sep)

        upgrade_btn = QPushButton("⬆️ Planı Yükselt →")
        upgrade_btn.setObjectName("primaryBtn")
        upgrade_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        upgrade_btn.clicked.connect(self._open_pricing)
        sub_layout.addWidget(upgrade_btn)

        manage_btn = QPushButton("📋 Aboneliği Yönet")
        manage_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        manage_btn.clicked.connect(self._open_dashboard)
        sub_layout.addWidget(manage_btn)

        layout.addWidget(sub_box)

        # ── Plan comparison ───────────────────────────────────
        plans_box = QGroupBox("Plan Karşılaştırması")
        plans_layout = QVBoxLayout(plans_box)

        for plan_id, plan in PLANS.items():
            row = QHBoxLayout()
            name_lbl = QLabel(f"{'⭐ ' if plan_id == 'pro' else ''}{plan['name']}")
            name_lbl.setMinimumWidth(80)
            row.addWidget(name_lbl)

            msg_text = "Sınırsız" if plan["messages"] == -1 else f"{plan['messages']} mesaj/ay"
            row.addWidget(QLabel(msg_text))
            row.addStretch()

            price_lbl = QLabel(f"₺{plan['price_try']} / ${plan['price_usd']}")
            price_lbl.setStyleSheet("color: #4F6EF7; font-weight: 600;")
            row.addWidget(price_lbl)

            plans_layout.addLayout(row)

        layout.addWidget(plans_box)

        # ── App info ──────────────────────────────────────────
        info_box = QGroupBox("Uygulama")
        info_layout = QVBoxLayout(info_box)

        info_layout.addWidget(QLabel(f"Versiyon: {APP_VERSION}"))

        docs_btn = QPushButton("📖 Kullanım Kılavuzu")
        docs_btn.setObjectName("ghostBtn")
        docs_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        docs_btn.clicked.connect(lambda: webbrowser.open("https://hsbvectoai.com/docs"))
        info_layout.addWidget(docs_btn)

        support_btn = QPushButton("💬 Destek")
        support_btn.setObjectName("ghostBtn")
        support_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        support_btn.clicked.connect(lambda: webbrowser.open("https://hsbvectoai.com/support"))
        info_layout.addWidget(support_btn)

        layout.addWidget(info_box)
        layout.addStretch()

        scroll.setWidget(content)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def refresh_license(self, license_data: dict):
        """Update UI with fresh license data."""
        plan_id = license_data.get("plan", "starter")
        plan_info = PLANS.get(plan_id, {})

        self._plan_lbl.setText(f"{plan_info.get('name', plan_id)} Plan")

        expires = license_data.get("expires_at", "—")
        self._status_lbl.setText(f"Yenileme tarihi: {expires}")

        messages_left = license_data.get("messages_left", -1)
        if messages_left == -1:
            self._messages_lbl.setText("Mesaj: Sınırsız")
        else:
            self._messages_lbl.setText(f"Kalan mesaj: {messages_left}")

    def _open_pricing(self):
        webbrowser.open("https://hsbvectoai.com/pricing")

    def _open_dashboard(self):
        webbrowser.open("https://hsbvectoai.com/dashboard")
