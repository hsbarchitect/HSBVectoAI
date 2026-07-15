"""
License router — device activation and verification.
Desktop app calls /verify on every launch.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from dependencies import get_current_user, require_active_subscription
from models.user import User
from services import license_service, usage_service

router = APIRouter(prefix="/license", tags=["license"])


class ActivateRequest(BaseModel):
    device_id: str
    device_name: str | None = None


class VerifyRequest(BaseModel):
    device_id: str


@router.post("/activate")
async def activate(
    req: ActivateRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_active_subscription),
):
    """Register a device against the user's subscription."""
    result = await license_service.activate_device(user, req.device_id, req.device_name, db)
    if not result["success"]:
        raise HTTPException(status_code=403, detail=result["error"])
    return {"message": "Cihaz başarıyla aktive edildi.", "device_id": req.device_id}


@router.post("/verify")
async def verify(
    req: VerifyRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Verify device + subscription — called by Desktop App on every launch.
    Also returns messages_left so the UI can show the usage bar.
    """
    status = await license_service.verify_device(user, req.device_id, db)
    if not status["valid"]:
        raise HTTPException(status_code=403, detail=status["error"])

    # Enrich with current month usage
    _, messages_left = await usage_service.check_limit(user, db)
    return {**status, "messages_left": messages_left}


@router.get("/status")
async def get_status(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Return subscription plan + usage stats."""
    _, messages_left = await usage_service.check_limit(user, db)
    devices = await license_service.list_devices(user.id, db)
    return {
        "plan": user.plan,
        "email": user.email,
        "messages_left": messages_left,
        "devices": devices,
    }


@router.delete("/device/{device_id}")
async def remove_device(
    device_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Unregister a device from the user's subscription."""
    success = await license_service.deactivate_device(user.id, device_id, db)
    if not success:
        raise HTTPException(status_code=404, detail="Cihaz bulunamadı.")
    return {"message": "Cihaz kaldırıldı."}
