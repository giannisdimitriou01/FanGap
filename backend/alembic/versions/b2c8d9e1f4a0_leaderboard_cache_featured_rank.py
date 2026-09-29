"""Revision: leaderboard_cache + games.featured_rank"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "b2c8d9e1f4a0"
down_revision: Union[str, None] = "a371a055324b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("games", sa.Column("featured_rank", sa.Integer(), nullable=True))
    op.create_index("ix_games_featured_rank", "games", ["featured_rank"], unique=False)
    op.create_table(
        "leaderboard_cache",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("pool_size", sa.Integer(), nullable=False),
        sa.Column(
            "built_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("leaderboard_cache")
    op.drop_index("ix_games_featured_rank", table_name="games")
    op.drop_column("games", "featured_rank")
