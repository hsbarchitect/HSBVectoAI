"""
AI Client — sends chat messages to HSBVectoAI backend.
Backend acts as a proxy to Gemini / OpenAI — no API keys on client.
"""

import requests
import logging
from typing import Generator, Optional

from app.core.config import API_BASE_URL, DEFAULT_MODEL

logger = logging.getLogger(__name__)

# CorelDRAW context injected into every conversation
SYSTEM_PROMPT = """Sen HSBVectoAI'sın — CorelDRAW için yapay zeka tasarım asistanı.
Kullanıcı senden CorelDRAW'da tasarım işlemleri yapmanı isteyebilir.
Mevcut araçların:
- Belge oluşturma (create_document)
- Şekil çizimi (draw_rectangle, draw_ellipse, draw_polygon, draw_star)
- Metin ekleme (add_text, add_artistic_text)
- Renk işlemleri (set_fill_color, set_outline_color, create_gradient)
- Efektler (add_drop_shadow, add_glow, add_blur, add_bevel)
- Arka plan silme (remove_background)
- Dışa aktarma (export_pdf, export_png, export_svg)

Türkçe ve İngilizce yanıt verebilirsin.
Her zaman net, pratik ve adım adım yönlendirme yap.
Bir komut çalıştırırken ne yaptığını kısaca açıkla."""


class AIClient:
    """HTTP client for HSBVectoAI backend AI proxy endpoint."""

    def __init__(self, auth_manager):
        self._auth = auth_manager
        self._model = DEFAULT_MODEL
        self._history: list[dict] = []

    def set_model(self, model_id: str) -> None:
        self._model = model_id

    def clear_history(self) -> None:
        self._history = []

    def send_message(
        self,
        message: str,
        corel_context: Optional[dict] = None,
        on_chunk: Optional[callable] = None,
    ) -> dict:
        """
        Send a message to the AI backend.

        Args:
            message: User's text message
            corel_context: Current CorelDRAW state (open doc, selected objects, etc.)
            on_chunk: Optional streaming callback (str chunk) → called per token

        Returns:
            {"success": bool, "reply": str, "actions": list, "error": str|None}
        """
        if not self._auth.is_logged_in:
            return {"success": False, "error": "Giriş yapılmamış."}

        # Build message history
        self._history.append({"role": "user", "content": message})

        payload = {
            "model": self._model,
            "messages": self._history,
            "system_prompt": SYSTEM_PROMPT,
            "corel_context": corel_context or {},
            "stream": on_chunk is not None,
        }

        try:
            if on_chunk:
                return self._stream_request(payload, on_chunk)
            else:
                return self._regular_request(payload)
        except requests.ConnectionError:
            return {"success": False, "error": "Sunucuya bağlanılamadı."}
        except Exception as e:
            logger.exception("AI request failed")
            return {"success": False, "error": str(e)}

    def _parse_actions(self, text: str) -> tuple[str, list]:
        import json
        if "[ACTIONS]" in text:
            parts = text.split("[ACTIONS]")
            clean_text = parts[0].strip()
            actions_str = parts[1].strip()
            try:
                start = actions_str.find("[")
                end = actions_str.rfind("]") + 1
                if start != -1 and end != -1:
                    actions = json.loads(actions_str[start:end])
                    return clean_text, actions
            except Exception as e:
                logger.error(f"Failed to parse actions: {e}")
            return clean_text, []
        return text, []

    def _regular_request(self, payload: dict) -> dict:
        resp = requests.post(
            f"{API_BASE_URL}/ai/chat",
            json=payload,
            headers={"Authorization": f"Bearer {self._auth.token}"},
            timeout=60,
        )
        if resp.status_code == 200:
            data = resp.json()
            reply = data.get("reply", "")
            clean_reply, actions = self._parse_actions(reply)
            self._history.append({"role": "assistant", "content": clean_reply})
            return {
                "success": True,
                "reply": clean_reply,
                "actions": actions,
            }
        elif resp.status_code == 429:
            return {"success": False, "error": "Aylık mesaj limitinize ulaştınız. Planınızı yükseltin."}
        else:
            return {"success": False, "error": resp.json().get("detail", "AI yanıt vermedi.")}

    def _stream_request(self, payload: dict, on_chunk: callable) -> dict:
        full_reply = ""
        with requests.post(
            f"{API_BASE_URL}/ai/chat",
            json=payload,
            headers={"Authorization": f"Bearer {self._auth.token}"},
            stream=True,
            timeout=120,
        ) as resp:
            if resp.status_code != 200:
                return {"success": False, "error": "Streaming başlatılamadı."}
            for line in resp.iter_lines():
                if line:
                    chunk = line.decode("utf-8").removeprefix("data: ")
                    if chunk == "[DONE]":
                        break
                    full_reply += chunk
                    # Don't send [ACTIONS] tokens to UI
                    if "[ACTIONS]" not in full_reply:
                        on_chunk(chunk)

        clean_reply, actions = self._parse_actions(full_reply)
        self._history.append({"role": "assistant", "content": clean_reply})
        return {"success": True, "reply": clean_reply, "actions": actions}

    @property
    def model(self) -> str:
        return self._model

    @property
    def history(self) -> list:
        return self._history
