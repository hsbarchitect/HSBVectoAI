"""
License service — device registration and verification.
"""

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from config import get_settings
from models.license import License
from models.user import User

settings = get_settings()


async def activate_device(user: User, device_id: str, device_name: str | None, db: AsyncSession) -> dict:
    """
    Register a new device for the user, respecting plan device limits.

    Returns:
        {"success": bool, "error": str | None}
    """
    # Check if already registered
    existing = await db.execute(
        select(License).where(License.user_id == user.id, License.device_id == device_id)
    )
    license_row = existing.scalar_one_or_none()

    if license_row:
        if license_row.is_active:
            return {"success": True, "error": None}
        # Reactivate
        license_row.is_active = True
        return {"success": True, "error": None}

    # Check device count
    count_result = await db.execute(
        select(func.count(License.id)).where(
            License.user_id == user.id, License.is_active == True
        )
    )
    active_count = count_result.scalar_one()
    device_limit = settings.get_device_limit(user.plan)

    if active_count >= device_limit:
        return {
            "success": False,
            "error": f"Cihaz limitine ulaştınız ({device_limit} cihaz). Planınızı yükseltin veya bir cihazı kaldırın.",
        }

    db.add(License(user_id=user.id, device_id=device_id, device_name=device_name))
    return {"success": True, "error": None}


async def verify_device(user: User, device_id: str, db: AsyncSession) -> dict:
    """
    Verify device is registered and subscription is valid.

    Returns the license status dict that desktop app expects.
    """
    result = await db.execute(
        select(License).where(
            License.user_id == user.id,
            License.device_id == device_id,
            License.is_active == True,
        )
    )
    license_row = result.scalar_one_or_none()

    if not license_row:
        return {"valid": False, "error": "Bu cihaz kayıtlı değil. Lütfen aktivasyon yapın."}

    if user.plan == "free":
        return {"valid": False, "error": "Aktif abonelik bulunamadı."}

    limit = settings.get_monthly_limit(user.plan)

    return {
        "plan": user.plan,
        "messages_left": limit,  # -1 = unlimited; usage checked at /ai/chat
        "valid": True,
        "error": None,
    }


async def list_devices(user_id: int, db: AsyncSession) -> list[dict]:
    """Return all active devices for a user."""
    result = await db.execute(
        select(License).where(License.user_id == user_id, License.is_active == True)
    )
    return [
        {"device_id": r.device_id, "device_name": r.device_name, "last_seen": r.last_seen}
        for r in result.scalars()
    ]


async def deactivate_device(user_id: int, device_id: str, db: AsyncSession) -> bool:
    """Deactivate (unregister) a device."""
    result = await db.execute(
        select(License).where(License.user_id == user_id, License.device_id == device_id)
    )
    row = result.scalar_one_or_none()
    if not row:
        return False
    row.is_active = False
    return True
