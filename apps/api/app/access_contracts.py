"""Request and response models of the local access token administration."""

from pydantic import Field

from app.contracts import StrictModel
from app.domain.access import Role


class TokenRequest(StrictModel):
    # Printable label only (no control characters); it names a person or device, not a secret.
    label: str = Field(min_length=1, max_length=48, pattern=r"^[^\x00-\x1f\x7f]+$")
    role: Role


class TokenView(StrictModel):
    id: str
    label: str
    role: Role
    created_at: str
    revoked_at: str | None
    last_used_at: str | None
    active: bool


class TokenCreated(TokenView):
    # Shown exactly once; only its keyed hash is stored.
    token: str


class TokenList(StrictModel):
    items: list[TokenView]
    maximum_active: int


class Identity(StrictModel):
    subject_id: str
    label: str
    role: Role
    bootstrap: bool
