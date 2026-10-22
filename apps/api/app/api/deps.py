import asyncio
import hmac
from collections.abc import Callable
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.bootstrap import Container
from app.capabilities import declared, is_enabled
from app.domain.access import BOOTSTRAP_SUBJECT, Principal, Role, acting_subject, allows

bearer = HTTPBearer(auto_error=False)


class ProtectiveDenial(HTTPException):
    """A refusal that protects data or resources; audited as operation.denied."""

    def __init__(self, detail: str):
        super().__init__(409, detail)


def get_container(request: Request) -> Container:
    return request.app.state.container


ContainerDep = Annotated[Container, Depends(get_container)]


async def resolve_principal(container: Container, token: str) -> Principal | None:
    """Bootstrap SPATIAL_TOKEN (admin) or an active personal token; None otherwise."""
    if hmac.compare_digest(token.encode("utf-8"), container.settings.token.encode("utf-8")):
        return Principal(subject_id=BOOTSTRAP_SUBJECT, role="admin", label="SPATIAL_TOKEN")
    return await asyncio.to_thread(container.access_tokens.resolve, token)


async def authorize(
    request: Request, credentials: HTTPAuthorizationCredentials | None = Depends(bearer)
) -> Principal:
    container = request.app.state.container
    settings, store, limiter = container.settings, container.store, container.limiter
    origin = request.headers.get("origin")
    if origin and origin not in settings.origins:
        await asyncio.to_thread(store.security_denial, "origin.denied")
        raise HTTPException(403, "origin not allowed")
    peer = request.client.host if request.client else "local"
    principal = await resolve_principal(container, credentials.credentials) if credentials else None
    if principal is None:
        retry = limiter.check("auth", peer)
        await asyncio.to_thread(store.security_denial, "rate.denied" if retry else "auth.denied")
        if retry:
            raise HTTPException(429, "request limit reached", headers={"Retry-After": str(retry)})
        raise HTTPException(401, "valid local access token required")
    request.state.principal = principal
    # Audit entries written while serving this request record who acted.
    acting_subject.set(principal.subject_id)
    category = "read" if request.method == "GET" else "write"
    retry = limiter.check(category, peer)
    if retry:
        await asyncio.to_thread(store.security_denial, "rate.denied")
        raise HTTPException(429, "request limit reached", headers={"Retry-After": str(retry)})
    return principal


protected = [Depends(authorize)]


class RoleCheck:
    """Minimum role of one route; runs after authorize and before any capability check."""

    def __init__(self, minimum: Role):
        self.minimum = minimum

    async def __call__(self, request: Request) -> None:
        principal: Principal = request.state.principal
        if not allows(principal.role, self.minimum):
            store = request.app.state.container.store
            await asyncio.to_thread(store.security_denial, "role.denied")
            raise HTTPException(403, f"role {self.minimum} required")


def require_role(minimum: Role):
    return Depends(RoleCheck(minimum))


def require_capability(capability_id: str):
    """Refuse a surface the active profile disables; listed after the role (401, 403 role)."""
    if not declared(capability_id):
        raise ValueError(f"undeclared capability {capability_id}")

    def check(request: Request):
        profile = request.app.state.container.settings.capability_profile
        if not is_enabled(capability_id, profile):
            raise HTTPException(403, f"capability {capability_id} is disabled in profile {profile}")

    return Depends(check)


class GatedRouter(APIRouter):
    """Authenticated router: each route must declare require_role; the capability runs last.

    Order of refusals: 401 without a valid token, 403 for the role, 403 for the profile.
    A route without a declared role fails at import time instead of defaulting open.
    """

    def __init__(self, capability: str | None = None, **kwargs: Any):
        super().__init__(dependencies=protected, **kwargs)
        self.capability_gate = [require_capability(capability)] if capability else []

    def add_api_route(self, path: str, endpoint: Callable[..., Any], **kwargs: Any) -> None:
        dependencies = list(kwargs.pop("dependencies", None) or [])
        if not any(isinstance(item.dependency, RoleCheck) for item in dependencies):
            raise TypeError(f"route {path} must declare a minimum role")
        kwargs["dependencies"] = [*dependencies, *self.capability_gate]
        super().add_api_route(path, endpoint, **kwargs)


viewer = [require_role("viewer")]
operator = [require_role("operator")]
admin = [require_role("admin")]
