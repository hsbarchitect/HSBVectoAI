"""
OpenAI service — streaming AI proxy for GPT models.
"""

import logging
from typing import AsyncGenerator

from openai import AsyncOpenAI

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
Her zaman net, pratik ve adım adım yönlendirme yap."""


def _build_messages(messages: list[dict], corel_context: dict) -> list[dict]:
    system = CORELDRAW_SYSTEM_PROMPT
    if corel_context:
        ctx = "\n".join(f"- {k}: {v}" for k, v in corel_context.items())
        system += f"\n\nMevcut CorelDRAW durumu:\n{ctx}"
    return [{"role": "system", "content": system}, *messages]


async def stream_openai(
    model_id: str,
    messages: list[dict],
    corel_context: dict,
) -> AsyncGenerator[str, None]:
    """Yield text chunks from OpenAI as SSE-compatible strings."""
    client = AsyncOpenAI(api_key=settings.openai_api_key)
    full_messages = _build_messages(messages, corel_context)

    async with client.chat.completions.stream(
        model=model_id,
        messages=full_messages,
    ) as stream:
        async for chunk in stream:
            delta = chunk.choices[0].delta.content if chunk.choices else None
            if delta:
                yield delta


async def complete_openai(
    model_id: str,
    messages: list[dict],
    corel_context: dict,
) -> tuple[str, int, int]:
    """
    Non-streaming completion.
    Returns: (reply_text, prompt_tokens, completion_tokens)
    """
    client = AsyncOpenAI(api_key=settings.openai_api_key)
    full_messages = _build_messages(messages, corel_context)

    response = await client.chat.completions.create(
        model=model_id,
        messages=full_messages,
    )
    reply = response.choices[0].message.content
    return reply, response.usage.prompt_tokens, response.usage.completion_tokens
