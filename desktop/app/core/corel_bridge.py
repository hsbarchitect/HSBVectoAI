"""
CorelDRAW bridge — wraps COM automation for the desktop app.
Thin wrapper around the existing coreldraw-mcp modules.
"""

import sys
import os
import logging
from typing import Optional, Any

logger = logging.getLogger(__name__)

# Add coreldraw-mcp src to path
COREL_MCP_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "..", "coreldraw-mcp"
)
if os.path.exists(COREL_MCP_PATH):
    sys.path.insert(0, COREL_MCP_PATH)


class CorelDRAWBridge:
    """
    Bridges the desktop app with CorelDRAW via COM automation.
    Falls back gracefully if CorelDRAW is not installed.
    """

    def __init__(self):
        self._client = None
        self._available = self._check_availability()

    def _check_availability(self) -> bool:
        try:
            import pythoncom
            pythoncom.CoInitialize()
            from src.coreldraw.client import CorelDRAWClient
            self._client = CorelDRAWClient.get()
            self._client.ensure_connected()
            return self._client.app is not None
        except Exception as e:
            logger.debug(f"Availability check failed: {e}")
            return False

    def refresh(self) -> bool:
        self._available = self._check_availability()
        return self._available

    def get_context(self) -> dict:
        """Return current CorelDRAW state as context dict for AI."""
        if not self._available or not self._client:
            return {"connected": False}
        try:
            import pythoncom
            pythoncom.CoInitialize()
            self._client.ensure_connected()
            app = self._client.app
            ctx = {"connected": True, "version": str(app.Version)}

            if app.Documents.Count > 0:
                doc = app.ActiveDocument
                page = doc.ActivePage
                
                # Get width and height safely
                width = 210.0
                height = 297.0
                try:
                    width = doc.DrawingPageWidth * 25.4 / 72
                    height = doc.DrawingPageHeight * 25.4 / 72
                except Exception:
                    try:
                        width = page.SizeWidth
                        height = page.SizeHeight
                        if doc.Unit == 4:  # Inches
                            width *= 25.4
                            height *= 25.4
                    except Exception:
                        pass

                ctx["document"] = {
                    "name": doc.Name,
                    "width_mm": round(width, 1),
                    "height_mm": round(height, 1),
                    "pages": doc.Pages.Count,
                    "objects": page.Shapes.Count if page else 0,
                }
                
                try:
                    if app.ActiveSelection and app.ActiveSelection.Shapes.Count > 0:
                        ctx["selection"] = {
                            "count": app.ActiveSelection.Shapes.Count,
                            "types": [
                                s.Type for s in app.ActiveSelection.Shapes
                            ],
                        }
                except Exception:
                    pass
            else:
                ctx["document"] = None

            return ctx
        except Exception as e:
            logger.warning(f"CorelDRAW context error: {e}")
            return {"connected": False, "error": str(e)}

    def execute_action(self, action: dict) -> dict:
        """
        Execute a CorelDRAW action returned by AI backend.
        action = {"tool": "draw_rectangle", "params": {...}}
        """
        tool = action.get("tool")
        params = action.get("params", {})

        try:
            if tool == "create_document":
                from src.coreldraw.document import create_document
                return create_document(**params)
            elif tool == "draw_rectangle":
                from src.coreldraw.shapes import draw_rectangle
                return draw_rectangle(**params)
            elif tool == "draw_ellipse":
                from src.coreldraw.shapes import draw_ellipse
                return draw_ellipse(**params)
            elif tool == "add_text":
                from src.coreldraw.text import add_text
                return add_text(**params)
            elif tool == "set_fill_color":
                from src.coreldraw.colors import set_fill_color
                return set_fill_color(**params)
            elif tool == "remove_background":
                from src.image.bg_removal import remove_background
                return remove_background(**params)
            elif tool == "export_pdf":
                from src.coreldraw.export import export_pdf
                return export_pdf(**params)
            else:
                return {"success": False, "error": f"Bilinmeyen araç: {tool}"}
        except ImportError:
            return {"success": False, "error": "CorelDRAW modülleri yüklenemedi."}
        except Exception as e:
            logger.exception(f"Action execute error: {tool}")
            return {"success": False, "error": str(e)}

    @property
    def is_available(self) -> bool:
        return self._available
