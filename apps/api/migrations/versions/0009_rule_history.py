"""Rule lifecycle timestamps and audit subject; rows created before 0009 stay NULL."""

import sqlalchemy as sa
from alembic import op

revision = "0009"
down_revision = "0008"
branch_labels = None
depends_on = None


def upgrade():
    # Nullable on purpose: the creation/revocation time of older rules is unknown and is
    # never backfilled with a fabricated value.
    with op.batch_alter_table("local_rules") as batch:
        batch.add_column(sa.Column("created_at", sa.String(40), nullable=True))
        batch.add_column(sa.Column("revoked_at", sa.String(40), nullable=True))
    with op.batch_alter_table("audit_events") as batch:
        batch.add_column(sa.Column("subject_id", sa.String(36), nullable=True))


def downgrade():
    raise RuntimeError("destructive downgrade is not supported")
