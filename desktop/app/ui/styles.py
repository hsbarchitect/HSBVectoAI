"""
HSBVectoAI — Global stylesheet
Dark, premium design with HSB brand colors.
"""

STYLESHEET = """
/* ─── Base ─────────────────────────────────────────── */
* {
    font-family: 'Segoe UI', 'Inter', sans-serif;
    color: #E8EAF6;
    selection-background-color: #4F6EF7;
}

QMainWindow, QWidget {
    background-color: #0D0E14;
}

/* ─── Scrollbars ────────────────────────────────────── */
QScrollBar:vertical {
    background: #14161F;
    width: 6px;
    border-radius: 3px;
}
QScrollBar::handle:vertical {
    background: #252840;
    border-radius: 3px;
    min-height: 40px;
}
QScrollBar::handle:vertical:hover { background: #4F6EF7; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }

/* ─── Buttons ───────────────────────────────────────── */
QPushButton {
    background: #1C1F2E;
    border: 1px solid #252840;
    border-radius: 8px;
    padding: 8px 16px;
    font-size: 13px;
    font-weight: 500;
}
QPushButton:hover { background: #252840; border-color: #4F6EF7; }
QPushButton:pressed { background: #1a1c2a; }

QPushButton#primaryBtn {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #4F6EF7, stop:1 #7C3AED);
    border: none;
    color: white;
    font-weight: 600;
    padding: 10px 20px;
    font-size: 14px;
}
QPushButton#primaryBtn:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #6480FF, stop:1 #8B50F5);
}
QPushButton#primaryBtn:disabled { opacity: 0.5; }

QPushButton#dangerBtn {
    background: #2A1414;
    border: 1px solid #EF4444;
    color: #EF4444;
}
QPushButton#dangerBtn:hover { background: #3A1A1A; }

QPushButton#ghostBtn {
    background: transparent;
    border: none;
    color: #6B7280;
    padding: 4px 8px;
}
QPushButton#ghostBtn:hover { color: #E8EAF6; }

/* ─── Line Edits ────────────────────────────────────── */
QLineEdit {
    background: #1C1F2E;
    border: 1px solid #252840;
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 13px;
    color: #E8EAF6;
}
QLineEdit:focus { border-color: #4F6EF7; }
QLineEdit::placeholder { color: #6B7280; }

/* ─── Text Edit (chat input) ────────────────────────── */
QTextEdit {
    background: #1C1F2E;
    border: 1px solid #252840;
    border-radius: 10px;
    padding: 10px 14px;
    font-size: 13px;
    color: #E8EAF6;
}
QTextEdit:focus { border-color: #4F6EF7; }

/* ─── Combo Box ─────────────────────────────────────── */
QComboBox {
    background: #1C1F2E;
    border: 1px solid #252840;
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 13px;
    min-width: 140px;
}
QComboBox:hover { border-color: #4F6EF7; }
QComboBox::drop-down { border: none; width: 24px; }
QComboBox QAbstractItemView {
    background: #14161F;
    border: 1px solid #252840;
    selection-background-color: #4F6EF7;
}

/* ─── Labels ────────────────────────────────────────── */
QLabel#titleLabel {
    font-size: 18px;
    font-weight: 700;
    color: #E8EAF6;
}
QLabel#subtitleLabel {
    font-size: 12px;
    color: #6B7280;
}
QLabel#sectionLabel {
    font-size: 11px;
    font-weight: 600;
    color: #4F6EF7;
    letter-spacing: 1px;
    text-transform: uppercase;
}

/* ─── Status Badge ──────────────────────────────────── */
QLabel#statusOnline {
    background: #0C2A22;
    color: #22D3A5;
    border: 1px solid #22D3A5;
    border-radius: 10px;
    padding: 2px 10px;
    font-size: 11px;
    font-weight: 600;
}
QLabel#statusOffline {
    background: #2A1414;
    color: #EF4444;
    border: 1px solid #EF4444;
    border-radius: 10px;
    padding: 2px 10px;
    font-size: 11px;
    font-weight: 600;
}
QLabel#statusWarning {
    background: #2A1E08;
    color: #F59E0B;
    border: 1px solid #F59E0B;
    border-radius: 10px;
    padding: 2px 10px;
    font-size: 11px;
    font-weight: 600;
}

/* ─── Tab Widget ────────────────────────────────────── */
QTabWidget::pane {
    border: 1px solid #252840;
    border-radius: 10px;
    background: #14161F;
}
QTabBar::tab {
    background: transparent;
    padding: 8px 16px;
    font-size: 13px;
    color: #6B7280;
    border-bottom: 2px solid transparent;
}
QTabBar::tab:selected {
    color: #4F6EF7;
    border-bottom: 2px solid #4F6EF7;
}
QTabBar::tab:hover:!selected { color: #E8EAF6; }

/* ─── Group Box ─────────────────────────────────────── */
QGroupBox {
    border: 1px solid #252840;
    border-radius: 10px;
    margin-top: 8px;
    padding: 12px;
    font-size: 12px;
    color: #6B7280;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 4px;
    color: #4F6EF7;
    font-weight: 600;
    font-size: 11px;
}

/* ─── Separator ─────────────────────────────────────── */
QFrame[frameShape="4"], QFrame[frameShape="5"] {
    color: #252840;
    height: 1px;
}

/* ─── Message bubbles (via HTML in QTextBrowser) ────── */
QTextBrowser {
    background: #0D0E14;
    border: none;
    font-size: 13px;
}
"""
