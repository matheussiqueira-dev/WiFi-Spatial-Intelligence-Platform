"""Personal access tokens with roles (only keyed hashes) and the actor of each audit entry."""

import sqlalchemy as sa
from alembic import op

revision = "0011"
down_revision = "0010"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "access_tokens",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("label", sa.String(48), nullable=False),
        sa.Column("role", sa.String(16), nullable=False),
        # HMAC-SHA256 of the token under a server key; the token itself is never stored.
        sa.Column("token_hash", sa.String(64), nullable=False),
        sa.Column("created_at", sa.String(40), nullable=False),
        sa.Column("revoked_at", sa.String(40), nullable=True),
        sa.Column("last_used_at", sa.String(40), nullable=True),
    )
    op.create_index("ix_access_tokens_token_hash", "access_tokens", ["token_hash"], unique=True)
    # Nullable: entries before 0011 and background work have no known actor.
    with op.batch_alter_table("audit_events") as batch:
        batch.add_column(sa.Column("actor_id", sa.String(36), nullable=True))


def downgrade():
    raise RuntimeError("destructive downgrade is not supported")
