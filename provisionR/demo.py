"""Read-only demo mode: refuses every request that could write state or hand out credentials."""

import os
import re
from collections.abc import Mapping

from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

DEMO_MODE_VARIABLE = "PROVISIONR_DEMO_MODE"
READ_METHODS = frozenset({"GET", "HEAD"})
# GET /api/v1/ks creates a machine with fresh passwords, and the export returns every password.
REFUSED_PATH_PREFIXES = ("/api/v1/ks", "/api/v1/machines")
REFUSAL_DETAIL = "provisionR is running as a read-only demo, so this action is disabled"


def demo_mode_from_environment(environ: Mapping[str, str] = os.environ) -> bool:
    return environ.get(DEMO_MODE_VARIABLE, "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def is_refused(method: str, path: str) -> bool:
    if method.upper() not in READ_METHODS:
        return True
    normalised = re.sub(r"/{2,}", "/", path)
    return normalised.startswith(REFUSED_PATH_PREFIXES)


class DemoModeMiddleware:
    """Answers 403 before routing, so no handler, validation or body parsing runs."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "http" and is_refused(scope["method"], scope["path"]):
            response = JSONResponse({"detail": REFUSAL_DETAIL}, status_code=403)
            await response(scope, receive, send)
            return
        await self.app(scope, receive, send)
