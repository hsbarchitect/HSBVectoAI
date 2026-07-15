"""
Application-wide configuration constants.
"""

APP_NAME = "HSBVectoAI"
APP_VERSION = "1.0.0"
APP_DISPLAY_NAME = "HSBVectoAI — Smart Design for CorelDRAW"

# Backend API
API_BASE_URL = "https://api.hsbvectoai.com"  # Production
# API_BASE_URL = "http://localhost:8000"       # Development

# Subscription plans
PLANS = {
    "starter": {"name": "Starter", "price_try": 199, "price_usd": 9, "messages": 500, "devices": 1},
    "pro":     {"name": "Pro",     "price_try": 399, "price_usd": 18, "messages": -1, "devices": 3},
    "studio":  {"name": "Studio",  "price_try": 799, "price_usd": 35, "messages": -1, "devices": 10},
}

# AI Models available
AI_MODELS = {
    "gemini-2.0-flash": {
        "name": "Gemini 2.0 Flash",
        "provider": "google",
        "description": "Hızlı & ekonomik",
        "icon": "🔵",
    },
    "gemini-2.5-pro": {
        "name": "Gemini 2.5 Pro",
        "provider": "google",
        "description": "En akıllı (Pro/Studio)",
        "icon": "⚡",
    },
    "gpt-4o": {
        "name": "GPT-4o",
        "provider": "openai",
        "description": "OpenAI en iyi model",
        "icon": "🟢",
    },
    "gpt-4o-mini": {
        "name": "GPT-4o Mini",
        "provider": "openai",
        "description": "OpenAI hızlı & ekonomik",
        "icon": "🟢",
    },
}

DEFAULT_MODEL = "gemini-2.0-flash"

# UI
WINDOW_MIN_WIDTH  = 420
WINDOW_MIN_HEIGHT = 600
WINDOW_DEFAULT_WIDTH  = 460
WINDOW_DEFAULT_HEIGHT = 780

# Colors — HSBVectoAI brand palette
COLOR_BG_DARK    = "#0D0E14"
COLOR_BG_CARD    = "#14161F"
COLOR_BG_INPUT   = "#1C1F2E"
COLOR_ACCENT     = "#4F6EF7"   # Royal blue
COLOR_ACCENT2    = "#7C3AED"   # Purple (secondary)
COLOR_SUCCESS    = "#22D3A5"
COLOR_WARNING    = "#F59E0B"
COLOR_DANGER     = "#EF4444"
COLOR_TEXT       = "#E8EAF6"
COLOR_TEXT_MUTED = "#6B7280"
COLOR_BORDER     = "#252840"

# Keyring service names
KEYRING_SERVICE = "HSBVectoAI"
KEYRING_TOKEN   = "auth_token"
KEYRING_EMAIL   = "user_email"
