"""Local access roles: an ordered hierarchy, the authenticated principal and the audit actor."""

from contextvars import ContextVar
from dataclasses import dataclass
from typing import Literal

Role = Literal["viewer", "operator", "admin"]
ROLES: tuple[Role, ...] = ("viewer", "operator", "admin")
# The bootstrap SPATIAL_TOKEN is an admin that cannot be listed or revoked through the API.
BOOTSTRAP_SUBJECT = "bootstrap"
# Personal tokens carry a fixed prefix so malformed bearer values skip the database lookup.
TOKEN_PREFIX = "wsp_"

# Subject of the request being served; read by the audit trail (never a token value).
acting_subject: ContextVar[str | None] = ContextVar("acting_subject", default=None)


def allows(role: Role, minimum: Role) -> bool:
    return ROLES.index(role) >= ROLES.index(minimum)


@dataclass(frozen=True)
class Principal:
    subject_id: str
    role: Role
    label: str

    @property
    def bootstrap(self) -> bool:
        return self.subject_id == BOOTSTRAP_SUBJECT
