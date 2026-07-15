from routers.auth import router as auth_router
from routers.license import router as license_router
from routers.ai import router as ai_router
from routers.stripe import router as stripe_router

__all__ = ["auth_router", "license_router", "ai_router", "stripe_router"]
