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

    response = await client.chat.completions.create(
        model=model_id,
        messages=full_messages,
        stream=True,
    )
    async for chunk in response:
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
