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
Bir komut çalıştırırken ne yaptığını kısaca açıkla.

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
