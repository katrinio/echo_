from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import RedirectResponse

from src.features.auth.security import is_authenticated


PUBLIC_PATHS = {
    "/login",
    "/logout",
    "/health",
    "/robots.txt",
}


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path

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
