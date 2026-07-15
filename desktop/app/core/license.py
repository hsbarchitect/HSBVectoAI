"""
License manager — verifies subscription status against backend.
License is tied to device fingerprint (machine GUID + hostname).
"""

import hashlib
import socket
import logging
import platform
import requests
from typing import Optional

from app.core.config import API_BASE_URL

logger = logging.getLogger(__name__)


def get_device_fingerprint() -> str:
    """Generate a stable device ID from machine GUID and hostname."""
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\Cryptography",
        )
        machine_guid, _ = winreg.QueryValueEx(key, "MachineGuid")
        winreg.CloseKey(key)
    except Exception:
        machine_guid = "unknown"

    hostname = socket.gethostname()
    raw = f"{machine_guid}-{hostname}-{platform.node()}"
    return hashlib.sha256(raw.encode()).hexdigest()[:32]


class LicenseManager:
    """Checks and caches subscription/license status."""

    def __init__(self, auth_manager):
        self._auth = auth_manager
        self._license_data: Optional[dict] = None
        self._device_id = get_device_fingerprint()

    def activate(self) -> bool:
        """Register this device with the backend."""
        try:
            resp = requests.post(
                f"{API_BASE_URL}/license/activate",
                json={"device_id": self._device_id, "device_name": socket.gethostname()},
                headers={"Authorization": f"Bearer {self._auth.token}"},
                timeout=8,
            )
            return resp.status_code == 200
        except Exception as e:
            logger.exception("License activation failed")
            return False

    def verify(self) -> dict:
        """
        Verify license with backend. Auto-activates device if not registered.
        """
        if not self._auth.is_logged_in:
            return {"valid": False, "error": "Giriş yapılmamış."}

        try:
            resp = requests.post(
                f"{API_BASE_URL}/license/verify",
                json={"device_id": self._device_id},
                headers={"Authorization": f"Bearer {self._auth.token}"},
                timeout=8,
            )
            if resp.status_code == 200:
                data = resp.json()
                self._license_data = data
                return {**data, "valid": True}
            elif resp.status_code == 403:
                detail = resp.json().get("detail", "")
                if "cihaz kayıtlı değil" in detail.lower():
                    logger.info("Device not registered. Attempting auto-activation...")
                    if self.activate():
                        # Retry verification after successful activation
                        return self.verify()
                return {"valid": False, "error": "Geçersiz lisans veya abonelik sona ermiş."}
            else:
                return {"valid": False, "error": resp.json().get("detail", "Lisans doğrulanamadı.")}
        except requests.ConnectionError:
            # Offline grace — use cached data if available
            if self._license_data:
                return {**self._license_data, "valid": True, "offline": True}
            return {"valid": False, "error": "Çevrimdışı — lisans önbelleği bulunamadı."}
        except Exception as e:
            logger.exception("License verify error")
            return {"valid": False, "error": str(e)}

    @property
    def device_id(self) -> str:
        return self._device_id

    @property
    def plan(self) -> Optional[str]:
        if self._license_data:
            return self._license_data.get("plan")
        return None

    @property
    def is_pro_or_above(self) -> bool:
        return self.plan in ("pro", "studio")
