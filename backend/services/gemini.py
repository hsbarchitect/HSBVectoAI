"""
Gemini service — streaming AI proxy for Google Gemini.
System prompt injects CorelDRAW context.
"""

import asyncio
import logging
from typing import AsyncGenerator

import google.generativeai as genai

from config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

CORELDRAW_SYSTEM_PROMPT = """Sen HSBVectoAI'sın — CorelDRAW için yapay zeka tasarım asistanı.
Kullanıcı senden CorelDRAW'da tasarım işlemleri yapmanı isteyebilir.

Her zaman kullanıcının istediği çizim/tasarım işlemlerini gerçekleştirmek için yanıtının en sonuna [ACTIONS] etiketi koy ve hemen altına geçerli bir JSON dizisi olarak çağrılacak araçları ve parametrelerini ekle. Parametrelerdeki ölçü birimleri aksi belirtilmedikçe milimetre (mm) olmalıdır.

Mevcut araçların ve parametreleri:
- create_document() -> Yeni boş belge oluşturur.
- draw_rectangle(x_mm, y_mm, width_mm, height_mm, corner_radius_mm=0, fill_color='#ffffff', outline_color='#000000', outline_width_mm=0.5, no_fill=False, no_outline=False) -> Dikdörtgen çizer.
- draw_ellipse(x_mm, y_mm, width_mm, height_mm, fill_color='#ffffff', outline_color='#000000', outline_width_mm=0.5, no_fill=False, no_outline=False) -> Daire/Elips çizer.
- add_text(text, x_mm, y_mm, font_name='Arial', font_size=12, fill_color='#000000') -> Sanatsal metin ekler.
- set_fill_color(fill_color) -> Seçili nesnenin iç rengini ayarlar.
- remove_background() -> Seçili nesnenin arka planını temizler.
- export_pdf(filepath) -> Belgeyi PDF olarak kaydeder.

Örnek çıktı formatı:
Açıklama metni buraya yazılacak...
[ACTIONS]
[
  {"tool": "draw_rectangle", "params": {"x_mm": 50, "y_mm": 50, "width_mm": 100, "height_mm": 100, "fill_color": "#ff0000", "outline_color": "#000000"}}
]

Türkçe ve İngilizce yanıt verebilirsin.
Her zaman net, pratik ve adım adım yönlendirme yap.
{corel_context}"""


def _build_system_prompt(corel_context: dict) -> str:
    if not corel_context:
        return CORELDRAW_SYSTEM_PROMPT.format(corel_context="")
    ctx_lines = "\n".join(f"- {k}: {v}" for k, v in corel_context.items())
    return CORELDRAW_SYSTEM_PROMPT.format(corel_context=f"\nMevcut CorelDRAW durumu:\n{ctx_lines}")


def _convert_history(messages: list[dict]) -> list[dict]:
    """Convert OpenAI-style history to Gemini format."""
    result = []
    for msg in messages:
        role = "model" if msg["role"] == "assistant" else "user"
        result.append({"role": role, "parts": [msg["content"]]})
    return result


async def stream_gemini(
    model_id: str,
    messages: list[dict],
    corel_context: dict,
) -> AsyncGenerator[str, None]:
    """Yield text chunks from Gemini as SSE-compatible strings."""
    genai.configure(api_key=settings.gemini_api_key)

    system_prompt = _build_system_prompt(corel_context)

    # Separate last user message for send_message
    history = _convert_history(messages[:-1])
    last_message = messages[-1]["content"] if messages else ""

    model = genai.GenerativeModel(
        model_name=model_id,
        system_instruction=system_prompt,
    )
    chat = model.start_chat(history=history)

    loop = asyncio.get_event_loop()

    def _sync_stream():
        return chat.send_message(last_message, stream=True)

    response = await loop.run_in_executor(None, _sync_stream)

    for chunk in response:
        if chunk.text:
            yield chunk.text


async def complete_gemini(
    model_id: str,
    messages: list[dict],
    corel_context: dict,
) -> tuple[str, int, int]:
    """
    Non-streaming completion.
    Returns: (reply_text, prompt_tokens, completion_tokens)
    """
    genai.configure(api_key=settings.gemini_api_key)

    system_prompt = _build_system_prompt(corel_context)
    history = _convert_history(messages[:-1])
    last_message = messages[-1]["content"] if messages else ""

    model = genai.GenerativeModel(model_name=model_id, system_instruction=system_prompt)
    chat = model.start_chat(history=history)

    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(None, lambda: chat.send_message(last_message))

    reply = response.text
    usage = response.usage_metadata
    return reply, getattr(usage, "prompt_token_count", 0), getattr(usage, "candidates_token_count", 0)
