"""Local access profiles: the caller's identity and admin-only personal token management."""

import asyncio

from fastapi import APIRouter, HTTPException, Request, Response

from app.access_contracts import Identity, TokenCreated, TokenList, TokenRequest
from app.adapters.sqlite.access import MAX_ACTIVE_TOKENS
from app.api.deps import ContainerDep, GatedRouter, admin, viewer
from app.domain.access import Principal

router: APIRouter = GatedRouter()


@router.get("/api/v1/access/me", response_model=Identity, dependencies=viewer)
def me(request: Request):
    principal: Principal = request.state.principal
    return Identity(
        subject_id=principal.subject_id,
        label=principal.label,
        role=principal.role,
        bootstrap=principal.bootstrap,
    )


@router.get("/api/v1/access/tokens", response_model=TokenList, dependencies=admin)
def tokens(c: ContainerDep):
    return TokenList(items=c.access_tokens.tokens(), maximum_active=MAX_ACTIVE_TOKENS)


@router.post(
    "/api/v1/access/tokens", response_model=TokenCreated, status_code=201, dependencies=admin
)
async def create_token(body: TokenRequest, c: ContainerDep, response: Response):
    try:
        view, token = await asyncio.to_thread(c.access_tokens.create, body.label, body.role)
    except ValueError as error:
        raise HTTPException(409, str(error)) from error
    # The only response that ever carries the token value; never cached.
    response.headers["Cache-Control"] = "no-store"
    return TokenCreated(**view, token=token)


@router.post("/api/v1/access/tokens/{identifier}/revoke", dependencies=admin)
async def revoke_token(identifier: str, c: ContainerDep):
    if not await asyncio.to_thread(c.access_tokens.revoke, identifier):
        raise HTTPException(404, "token not found")
    return {"revoked": True}
