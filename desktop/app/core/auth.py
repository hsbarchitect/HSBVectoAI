"""
Auth manager — handles login, token storage, and session.
Tokens stored securely in Windows Credential Manager via keyring.
"""

import keyring
import requests
import logging
from typing import Optional

from app.core.config import API_BASE_URL, KEYRING_SERVICE, KEYRING_TOKEN, KEYRING_EMAIL

logger = logging.getLogger(__name__)


class AuthManager:
    """Manages authentication tokens and user session."""

    def __init__(self):
        self._token: Optional[str] = None
        self._email: Optional[str] = None
        self._user_data: Optional[dict] = None

    # ── Token persistence ─────────────────────────────────────

    def save_token(self, token: str, email: str) -> None:
        keyring.set_password(KEYRING_SERVICE, KEYRING_TOKEN, token)
        keyring.set_password(KEYRING_SERVICE, KEYRING_EMAIL, email)
        self._token = token
        self._email = email

    def load_token(self) -> bool:
        """Load saved token from credential manager. Returns True if found."""
        token = keyring.get_password(KEYRING_SERVICE, KEYRING_TOKEN)
        email = keyring.get_password(KEYRING_SERVICE, KEYRING_EMAIL)
        if token and email:
            self._token = token
            self._email = email
            return True
        return False

    def clear_token(self) -> None:
        try:
            keyring.delete_password(KEYRING_SERVICE, KEYRING_TOKEN)
            keyring.delete_password(KEYRING_SERVICE, KEYRING_EMAIL)
        except Exception:
            pass
        self._token = None
        self._email = None
        self._user_data = None

    # ── Login / Register ──────────────────────────────────────

    def login(self, email: str, password: str) -> dict:
        """Login with email/password. Returns {success, user, error}."""
        try:
            resp = requests.post(
                f"{API_BASE_URL}/auth/login",
                json={"email": email, "password": password},
                timeout=10,
            )
            if resp.status_code == 200:
                data = resp.json()
                self.save_token(data["access_token"], email)
                self._user_data = data.get("user", {})
                return {"success": True, "user": self._user_data}
            else:
                msg = resp.json().get("detail", "Giriş başarısız.")
                return {"success": False, "error": msg}
        except requests.ConnectionError:
            return {"success": False, "error": "Sunucuya bağlanılamadı. İnternet bağlantınızı kontrol edin."}
        except Exception as e:
            logger.exception("Login error")
            return {"success": False, "error": str(e)}

    def logout(self) -> None:
        try:
            requests.post(
                f"{API_BASE_URL}/auth/logout",
                headers=self._auth_headers(),
                timeout=5,
            )
        except Exception:
            pass
        self.clear_token()

    # ── Session validation ────────────────────────────────────

    def validate_session(self) -> dict:
        """Check if stored token is still valid. Returns {valid, user}."""
        if not self._token:
            return {"valid": False}
        try:
            resp = requests.get(
                f"{API_BASE_URL}/auth/me",
                headers=self._auth_headers(),
                timeout=8,
            )
            if resp.status_code == 200:
                self._user_data = resp.json()
                return {"valid": True, "user": self._user_data}
            self.clear_token()
            return {"valid": False}
        except Exception:
            # Offline — allow cached session
            if self._user_data:
                return {"valid": True, "user": self._user_data, "offline": True}
            return {"valid": False}

    # ── Helpers ───────────────────────────────────────────────

    def _auth_headers(self) -> dict:
        return {"Authorization": f"Bearer {self._token}"}

    @property
    def token(self) -> Optional[str]:
        return self._token

    @property
    def email(self) -> Optional[str]:
        return self._email

    @property
    def user_data(self) -> Optional[dict]:
        return self._user_data

    @property
    def is_logged_in(self) -> bool:
        return self._token is not None
