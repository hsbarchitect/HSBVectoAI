"""
Usage service — tracks and enforces monthly AI message limits.
"""

from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from config import get_settings
from models.ai_usage import AiUsage
from models.user import User

settings = get_settings()


async def get_monthly_usage(user_id: int, db: AsyncSession) -> int:
    """Count messages used this calendar month."""
    now = datetime.now(timezone.utc)
    # PostgreSQL column is TIMESTAMP WITHOUT TIME ZONE — use naive datetime
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0, tzinfo=None)

    result = await db.execute(
        select(func.count(AiUsage.id)).where(
            AiUsage.user_id == user_id,
            AiUsage.created_at >= month_start,
        )
    )
    return result.scalar_one()


async def check_limit(user: User, db: AsyncSession) -> tuple[bool, int]:
    """
    Check if user can send another message.

    Returns:
        (allowed: bool, messages_left: int)  -1 = unlimited
    """
    limit = settings.get_monthly_limit(user.plan)
    if limit == -1:
        return True, -1

    used = await get_monthly_usage(user.id, db)
    left = max(0, limit - used)
    return left > 0, left


async def record_usage(
    user_id: int,
    model: str,
    prompt_tokens: int,
    completion_tokens: int,
    db: AsyncSession,
) -> None:
    """Record an AI call in the database."""
    usage = AiUsage(
        user_id=user_id,
        model=model,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
    )
    db.add(usage)
    await db.flush()
