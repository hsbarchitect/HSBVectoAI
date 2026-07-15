"""
Chat panel — main AI conversation interface.
Streaming responses shown token-by-token.
CorelDRAW actions executed automatically after AI response.
"""

import re
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTextBrowser, QTextEdit, QLabel, QComboBox, QSizePolicy
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QKeyEvent

from app.core.config import AI_MODELS, COLOR_ACCENT


# ── Worker thread ──────────────────────────────────────────────

class ChatWorker(QThread):
    """Runs AI request in background and emits streamed tokens."""
    chunk_received = pyqtSignal(str)
    finished = pyqtSignal(dict)

    def __init__(self, ai_client, message, corel_context):
        super().__init__()
        self._ai = ai_client
        self._message = message
        self._context = corel_context

    def run(self):
        result = self._ai.send_message(
            self._message,
            corel_context=self._context,
            on_chunk=lambda chunk: self.chunk_received.emit(chunk),
        )
        self.finished.emit(result)


# ── Chat input ─────────────────────────────────────────────────

class ChatInput(QTextEdit):
    """Multi-line input that sends on Enter (Shift+Enter for newline)."""
    send_requested = pyqtSignal()

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            if event.modifiers() == Qt.KeyboardModifier.ShiftModifier:
                super().keyPressEvent(event)
            else:
                self.send_requested.emit()
        else:
            super().keyPressEvent(event)


# ── Chat panel ─────────────────────────────────────────────────

class ChatPanel(QWidget):
    """Full chat UI with message history, model selector, and send button."""

    action_requested = pyqtSignal(dict)  # emits CorelDRAW action dicts

    def __init__(self, ai_client, corel_bridge, parent=None):
        super().__init__(parent)
        self._ai = ai_client
        self._corel = corel_bridge
        self._worker = None
        self._is_streaming = False
        self._current_ai_html = ""

        self._build_ui()
        self._show_welcome()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        # ── Top bar ──────────────────────────────────────────
        top_bar = QWidget()
        top_bar.setFixedHeight(52)
        top_bar.setStyleSheet("background: #14161F; border-bottom: 1px solid #252840;")
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(16, 0, 16, 0)

        self._corel_status = QLabel("⬤ CorelDRAW Bağlı")
        self._corel_status.setObjectName("statusOnline")
        top_layout.addWidget(self._corel_status)

        top_layout.addStretch()

        model_lbl = QLabel("Model:")
        model_lbl.setObjectName("subtitleLabel")
        top_layout.addWidget(model_lbl)

        self._model_combo = QComboBox()
        for model_id, info in AI_MODELS.items():
            self._model_combo.addItem(f"{info['icon']} {info['name']}", model_id)
        self._model_combo.currentIndexChanged.connect(self._on_model_changed)
        top_layout.addWidget(self._model_combo)

        clear_btn = QPushButton("🗑")
        clear_btn.setObjectName("ghostBtn")
        clear_btn.setToolTip("Sohbeti temizle")
        clear_btn.setFixedSize(32, 32)
        clear_btn.clicked.connect(self._clear_chat)
        top_layout.addWidget(clear_btn)

        layout.addWidget(top_bar)

        # ── Message area ──────────────────────────────────────
        self._chat_display = QTextBrowser()
        self._chat_display.setOpenExternalLinks(True)
        self._chat_display.setReadOnly(True)
        self._chat_display.setStyleSheet("""
            QTextBrowser {
                background: #0D0E14;
                border: none;
                padding: 16px;
                font-size: 13px;
                line-height: 1.6;
            }
        """)
        layout.addWidget(self._chat_display, stretch=1)

        # ── Typing indicator ──────────────────────────────────
        self._typing_bar = QWidget()
        self._typing_bar.setFixedHeight(28)
        self._typing_bar.setStyleSheet("background: #0D0E14;")
        typing_layout = QHBoxLayout(self._typing_bar)
        typing_layout.setContentsMargins(16, 0, 16, 0)
        self._typing_lbl = QLabel("HSBVectoAI yazıyor…")
        self._typing_lbl.setObjectName("subtitleLabel")
        typing_layout.addWidget(self._typing_lbl)
        typing_layout.addStretch()
        self._typing_bar.hide()
        layout.addWidget(self._typing_bar)

        # ── Input area ────────────────────────────────────────
        input_area = QWidget()
        input_area.setStyleSheet("background: #14161F; border-top: 1px solid #252840;")
        input_layout = QHBoxLayout(input_area)
        input_layout.setContentsMargins(12, 10, 12, 10)
        input_layout.setSpacing(10)

        self._input = ChatInput()
        self._input.setPlaceholderText("CorelDRAW'da ne yapmak istiyorsun?  (Enter = gönder, Shift+Enter = yeni satır)")
        self._input.setFixedHeight(80)
        self._input.send_requested.connect(self._send_message)
        input_layout.addWidget(self._input, stretch=1)

        self._send_btn = QPushButton("➤")
        self._send_btn.setObjectName("primaryBtn")
        self._send_btn.setFixedSize(48, 48)
        self._send_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._send_btn.clicked.connect(self._send_message)
        input_layout.addWidget(self._send_btn, alignment=Qt.AlignmentFlag.AlignBottom)

        layout.addWidget(input_area)

    # ── Chat logic ─────────────────────────────────────────────

    def _show_welcome(self):
        html = """
        <div style='text-align:center; padding: 40px 20px;'>
            <div style='font-size:48px;'>⚡</div>
            <div style='font-size:22px; font-weight:700; color:#E8EAF6; margin:12px 0 6px;'>HSBVectoAI</div>
            <div style='font-size:13px; color:#6B7280;'>Smart Design for CorelDRAW</div>
            <div style='margin-top:28px;'></div>
            <div style='font-size:12px; color:#4F6EF7; font-weight:600; letter-spacing:1px;'>ÖRNEK KOMUTLAR</div>
            <div style='margin-top:12px;'>
                <div class='suggestion' onclick=''>💠 A4 belgesi oluştur, kırmızı arka plan ekle</div>
                <div class='suggestion'>📝 Ortaya "MERHABA DÜNYA" yaz, mavi renk</div>
                <div class='suggestion'>🔶 10x10 cm sarı dikdörtgen çiz, gölge efekti ekle</div>
                <div class='suggestion'>🖼️ Seçili nesnenin arka planını sil</div>
            </div>
        </div>
        <style>
            .suggestion {
                background: #14161F;
                border: 1px solid #252840;
                border-radius: 8px;
                padding: 10px 16px;
                margin: 6px 0;
                cursor: pointer;
                color: #E8EAF6;
                font-size: 13px;
                text-align: left;
            }
            .suggestion:hover { border-color: #4F6EF7; }
        </style>
        """
        self._chat_display.setHtml(html)

    def _send_message(self):
        if self._is_streaming:
            return
        text = self._input.toPlainText().strip()
        if not text:
            return

        self._input.clear()
        self._append_user_message(text)
        self._start_ai_response()

        corel_ctx = self._corel.get_context() if self._corel else {}
        self._worker = ChatWorker(self._ai, text, corel_ctx)
        self._worker.chunk_received.connect(self._on_chunk)
        self._worker.finished.connect(self._on_response_done)
        self._worker.start()

    def _append_user_message(self, text: str):
        time_str = datetime.now().strftime("%H:%M")
        escaped = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")
        html_block = f"""
        <div style='margin: 12px 0; display:flex; justify-content:flex-end;'>
            <div style='max-width:80%; background:#1C2A4A; border-radius:16px 16px 4px 16px;
                        padding:10px 14px; color:#E8EAF6; font-size:13px;'>
                {escaped}
                <div style='font-size:10px; color:#6B7280; margin-top:4px; text-align:right;'>{time_str}</div>
            </div>
        </div>"""
        cursor = self._chat_display.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self._chat_display.setTextCursor(cursor)
        self._chat_display.insertHtml(html_block)
        self._scroll_bottom()

    def _start_ai_response(self):
        self._is_streaming = True
        self._send_btn.setEnabled(False)
        self._typing_bar.show()
        self._current_ai_html = ""
        # Placeholder for streaming response
        time_str = datetime.now().strftime("%H:%M")
        self._ai_bubble_start = f"""
        <div id='aiMsg' style='margin: 12px 0;'>
            <div style='display:flex; align-items:flex-start; gap:8px;'>
                <div style='font-size:20px;'>⚡</div>
                <div style='max-width:85%; background:#14161F; border:1px solid #252840;
                            border-radius:4px 16px 16px 16px;
                            padding:10px 14px; color:#E8EAF6; font-size:13px; line-height:1.6;'>"""
        self._ai_bubble_end = f"""
                    <div style='font-size:10px; color:#6B7280; margin-top:6px;'>{time_str}</div>
                </div>
            </div>
        </div>"""
        self._scroll_bottom()

    def _on_chunk(self, chunk: str):
        self._current_ai_html += chunk
        self._update_ai_bubble()

    def _update_ai_bubble(self):
        # Re-render entire chat with current streaming text
        # For simplicity, append streamed text directly
        pass  # Full streaming handled in _on_response_done for now

    def _on_response_done(self, result: dict):
        self._is_streaming = False
        self._send_btn.setEnabled(True)
        self._typing_bar.hide()

        if result.get("success"):
            reply = result.get("reply", "")
            self._append_ai_message(reply)

            # Execute any CorelDRAW actions
            for action in result.get("actions", []):
                self.action_requested.emit(action)
        else:
            error = result.get("error", "Bilinmeyen hata.")
            self._append_error_message(error)

        self._scroll_bottom()

    def _append_ai_message(self, text: str):
        time_str = datetime.now().strftime("%H:%M")
        # Convert markdown-ish to HTML
        html_text = self._markdown_to_html(text)
        html_block = f"""
        <div style='margin: 12px 0;'>
            <div style='display:flex; align-items:flex-start; gap:8px;'>
                <div style='font-size:20px;'>⚡</div>
                <div style='max-width:85%; background:#14161F; border:1px solid #252840;
                            border-radius:4px 16px 16px 16px;
                            padding:12px 14px; color:#E8EAF6; font-size:13px; line-height:1.6;'>
                    {html_text}
                    <div style='font-size:10px; color:#6B7280; margin-top:6px;'>{time_str}</div>
                </div>
            </div>
        </div>"""
        cursor = self._chat_display.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self._chat_display.setTextCursor(cursor)
        self._chat_display.insertHtml(html_block)

    def _append_error_message(self, error: str):
        html_block = f"""
        <div style='margin: 8px 16px;'>
            <div style='background:#2A1414; border:1px solid #EF4444; border-radius:8px;
                        padding:10px 14px; color:#EF4444; font-size:12px;'>
                ⚠️ {error}
            </div>
        </div>"""
        cursor = self._chat_display.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self._chat_display.setTextCursor(cursor)
        self._chat_display.insertHtml(html_block)

    def _clear_chat(self):
        self._ai.clear_history()
        self._show_welcome()

    def _scroll_bottom(self):
        sb = self._chat_display.verticalScrollBar()
        sb.setValue(sb.maximum())

    def _on_model_changed(self, index: int):
        model_id = self._model_combo.itemData(index)
        self._ai.set_model(model_id)

    def _markdown_to_html(self, text: str) -> str:
        """Simple markdown → HTML converter for chat bubbles."""
        text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        # Code blocks
        text = re.sub(r"```(.*?)```", r"<code style='background:#1C1F2E;border-radius:4px;padding:2px 6px;'>\1</code>", text, flags=re.DOTALL)
        # Bold
        text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", text)
        # Italic
        text = re.sub(r"\*(.*?)\*", r"<i>\1</i>", text)
        # Inline code
        text = re.sub(r"`(.*?)`", r"<code style='background:#1C1F2E;border-radius:4px;padding:1px 4px;font-size:12px;'>\1</code>", text)
        # Newlines
        text = text.replace("\n", "<br>")
        return text

    def update_corel_status(self, connected: bool):
        if connected:
            self._corel_status.setText("⬤ CorelDRAW Bağlı")
            self._corel_status.setObjectName("statusOnline")
        else:
            self._corel_status.setText("⬤ CorelDRAW Kapalı")
            self._corel_status.setObjectName("statusOffline")
        # Force style refresh
        self._corel_status.style().unpolish(self._corel_status)
        self._corel_status.style().polish(self._corel_status)
