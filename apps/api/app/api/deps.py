import asyncio
import hmac
from typing import Annotated

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.bootstrap import Container

bearer = HTTPBearer(auto_error=False)


def get_container(request: Request) -> Container:
    return request.app.state.container


ContainerDep = Annotated[Container, Depends(get_container)]


async def authorize(
    request: Request, credentials: HTTPAuthorizationCredentials | None = Depends(bearer)
):
    container = request.app.state.container
    settings, store, limiter = container.settings, container.store, container.limiter
    origin = request.headers.get("origin")
    if origin and origin not in settings.origins:
        await asyncio.to_thread(store.security_denial, "origin.denied")
        raise HTTPException(403, "origin not allowed")
    peer = request.client.host if request.client else "local"
    if not credentials or not hmac.compare_digest(
        credentials.credentials.encode("utf-8"), settings.token.encode("utf-8")
    ):
        retry = limiter.check("auth", peer)
        await asyncio.to_thread(store.security_denial, "rate.denied" if retry else "auth.denied")
        if retry:
            raise HTTPException(429, "request limit reached", headers={"Retry-After": str(retry)})
        raise HTTPException(401, "valid local development token required")
    category = "read" if request.method == "GET" else "write"
    retry = limiter.check(category, peer)
    if retry:
        await asyncio.to_thread(store.security_denial, "rate.denied")
        raise HTTPException(429, "request limit reached", headers={"Retry-After": str(retry)})


protected = [Depends(authorize)]
