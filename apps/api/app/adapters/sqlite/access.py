"""Personal access tokens: keyed hashes only, revocation keeps the row, audited lifecycle."""

import hashlib
import hmac
import secrets
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from sqlalchemy import select

from app.adapters.sqlite.database import Database, row_count
from app.adapters.sqlite.models import AccessTokenRow, audit_row
from app.domain.access import ROLES, TOKEN_PREFIX, Principal, Role

MAX_ACTIVE_TOKENS = 50
# Revoked rows are kept for the audit trail; the total is bounded as well.
MAX_TOKEN_ROWS = 500
# last_used_at is advisory; refreshing it at most once a minute avoids a write per request.
TOUCH_INTERVAL = timedelta(seconds=60)


def token_view(row: AccessTokenRow) -> dict:
    return {
        "id": row.id,
        "label": row.label,
        "role": row.role,
        "created_at": row.created_at,
        "revoked_at": row.revoked_at,
        "last_used_at": row.last_used_at,
        "active": row.revoked_at is None,
    }


class AccessTokenRepository:
    def __init__(self, database: Database, key: bytes):
        if len(key) < 32:
            raise ValueError("access token key must have at least 32 bytes")
        self.session = database.session
        self.key = key

    def digest(self, token: str) -> str:
        # HMAC under a server key: a copied database alone cannot test candidate tokens.
        return hmac.new(self.key, token.encode("utf-8"), hashlib.sha256).hexdigest()

    def create(self, label: str, role: Role) -> tuple[dict, str]:
        if role not in ROLES:
            raise ValueError("unknown role")
        token = TOKEN_PREFIX + secrets.token_urlsafe(32)
        with self.session.begin() as session:
            if row_count(session, AccessTokenRow) >= MAX_TOKEN_ROWS:
                raise ValueError(f"maximum {MAX_TOKEN_ROWS} token records")
            active = session.scalars(
                select(AccessTokenRow.id).where(AccessTokenRow.revoked_at.is_(None))
            ).all()
            if len(active) >= MAX_ACTIVE_TOKENS:
                raise ValueError(f"maximum {MAX_ACTIVE_TOKENS} active tokens; revoke one first")
            row = AccessTokenRow(
                id=str(uuid4()),
                label=label,
                role=role,
                token_hash=self.digest(token),
                created_at=datetime.now(UTC).isoformat(),
            )
            session.add(row)
            session.add(audit_row("access.token.created", row.id))
            return token_view(row), token

    def tokens(self) -> list[dict]:
        with self.session() as session:
            rows = session.scalars(select(AccessTokenRow).order_by(AccessTokenRow.created_at))
            return [token_view(row) for row in rows]

    def revoke(self, identifier: str) -> bool:
        with self.session.begin() as session:
            row = session.get(AccessTokenRow, identifier)
            if row is None:
                return False
            if row.revoked_at is None:
                row.revoked_at = datetime.now(UTC).isoformat()
                session.add(audit_row("access.token.revoked", row.id))
            return True

    def resolve(self, token: str) -> Principal | None:
        if not token.startswith(TOKEN_PREFIX) or len(token) > 128:
            return None
        digest = self.digest(token)
        with self.session.begin() as session:
            row = session.scalars(
                select(AccessTokenRow).where(AccessTokenRow.token_hash == digest)
            ).first()
            if row is None or row.revoked_at is not None or row.role not in ROLES:
                return None
            now = datetime.now(UTC)
            if row.last_used_at is None or (
                now - datetime.fromisoformat(row.last_used_at) >= TOUCH_INTERVAL
            ):
                row.last_used_at = now.isoformat()
            role: Role = ROLES[ROLES.index(row.role)]
            return Principal(subject_id=row.id, role=role, label=row.label)

    def active(self, identifier: str) -> bool:
        with self.session() as session:
            row = session.get(AccessTokenRow, identifier)
            return row is not None and row.revoked_at is None
