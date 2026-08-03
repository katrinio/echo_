from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import RedirectResponse

from src.features.auth.security import is_authenticated


PUBLIC_PATHS = {
    "/login",
    "/logout",
    "/health",
    "/manifest.webmanifest",
    "/robots.txt",
    "/sw.js",
}


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.scope.get("path", request.url.path)
        root_path = request.scope.get("root_path", "")
        if root_path and path.startswith(root_path):
            path = path.removeprefix(root_path) or "/"

        if path.startswith("/static/"):
            return await call_next(request)

        if path in PUBLIC_PATHS:
            return await call_next(request)

        if is_authenticated(request):
            return await call_next(request)

        return RedirectResponse(
            url=f"/login?next={path}",
            status_code=303,
        )
