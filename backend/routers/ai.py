"""
AI router — Gemini + OpenAI proxy with SSE streaming.
Matches desktop app's AIClient contract exactly.

POST /ai/chat
Body: {model, messages, system_prompt, corel_context, stream}
Response (streaming): SSE lines: "data: <chunk>\n\n" ... "data: [DONE]\n\n"
Response (regular):   {"reply": str, "actions": []}
"""

import asyncio
import logging
from typing import AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from dependencies import get_current_user
from models.user import User
from services import usage_service
from services.gemini import stream_gemini, complete_gemini
from services.openai_service import stream_openai, complete_openai

router = APIRouter(prefix="/ai", tags=["ai"])
logger = logging.getLogger(__name__)

# Supported models
GEMINI_MODELS = {
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-1.5-pro",
}
OPENAI_MODELS = {
    "gpt-4o-mini",
    "gpt-4o",
    "gpt-4-turbo",
}


class ChatRequest(BaseModel):
    model: str = "gemini-2.0-flash"
    messages: list[dict]               # [{role: user|assistant, content: str}]
    system_prompt: str | None = None   # ignored — backend uses its own system prompt
    corel_context: dict = {}
    stream: bool = False


async def _sse_generator(
    model: str,
    messages: list[dict],
    corel_context: dict,
    user_id: int,
    db: AsyncSession,
) -> AsyncGenerator[str, None]:
    """Yields SSE lines for streaming response."""
    full_reply = ""
    try:
        if model in GEMINI_MODELS:
            gen = stream_gemini(model, messages, corel_context)
        else:
            gen = stream_openai(model, messages, corel_context)

        async for chunk in gen:
            full_reply += chunk
            yield f"data: {chunk}\n\n"

        yield "data: [DONE]\n\n"

        # Record usage (approximate tokens)
        await usage_service.record_usage(
            user_id=user_id,
            model=model,
            prompt_tokens=sum(len(m["content"]) // 4 for m in messages),
            completion_tokens=len(full_reply) // 4,
            db=db,
        )
    except Exception as e:
        logger.exception("Streaming error")
        yield f"data: [ERROR] {str(e)}\n\n"


@router.post("/chat")
async def chat(
    req: ChatRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Main AI chat endpoint — supports both streaming (SSE) and regular responses."""

    # Validate model
    if req.model not in GEMINI_MODELS | OPENAI_MODELS:
        raise HTTPException(status_code=400, detail=f"Desteklenmeyen model: {req.model}")

    # Check message limit
    allowed, messages_left = await usage_service.check_limit(user, db)
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail="Aylık mesaj limitinize ulaştınız. Planınızı yükseltin.",
        )

    if req.stream:
        return StreamingResponse(
            _sse_generator(req.model, req.messages, req.corel_context, user.id, db),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
            },
        )

    # Regular (non-streaming) response
    try:
        if req.model in GEMINI_MODELS:
            reply, pt, ct = await complete_gemini(req.model, req.messages, req.corel_context)
        else:
            reply, pt, ct = await complete_openai(req.model, req.messages, req.corel_context)
    except Exception as e:
        logger.exception("AI completion error")
        raise HTTPException(status_code=502, detail=f"AI yanıt vermedi: {str(e)}")

    await usage_service.record_usage(user.id, req.model, pt, ct, db)

    return {"reply": reply, "actions": []}


@router.get("/models")
async def list_models(user: User = Depends(get_current_user)):
    """Return available models based on user plan."""
    models = [
        {"id": "gemini-2.0-flash", "name": "Gemini 2.0 Flash", "provider": "google", "plans": ["starter", "pro", "studio"]},
        {"id": "gemini-2.0-flash-lite", "name": "Gemini 2.0 Flash Lite", "provider": "google", "plans": ["starter", "pro", "studio"]},
        {"id": "gemini-1.5-pro", "name": "Gemini 1.5 Pro", "provider": "google", "plans": ["pro", "studio"]},
        {"id": "gpt-4o-mini", "name": "GPT-4o Mini", "provider": "openai", "plans": ["starter", "pro", "studio"]},
        {"id": "gpt-4o", "name": "GPT-4o", "provider": "openai", "plans": ["pro", "studio"]},
    ]
    # Filter by plan
    available = [m for m in models if user.plan in m["plans"]]
    return {"models": available}
