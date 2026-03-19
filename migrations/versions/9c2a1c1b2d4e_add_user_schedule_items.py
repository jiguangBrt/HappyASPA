"""add user schedule items

Revision ID: 9c2a1c1b2d4e
Revises: a4003bbafb0f
Create Date: 2026-03-16 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "9c2a1c1b2d4e"
down_revision = "a4003bbafb0f"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "user_schedule_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("scheduled_date", sa.Date(), nullable=False),
        sa.Column("kind", sa.String(length=30), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_user_schedule_items_user_id_scheduled_date",
        "user_schedule_items",
        ["user_id", "scheduled_date"],
    )
    op.create_index(
        op.f("ix_user_schedule_items_scheduled_date"),
        "user_schedule_items",
        ["scheduled_date"],
    )


def downgrade():
    op.drop_index(
        op.f("ix_user_schedule_items_scheduled_date"), table_name="user_schedule_items"
    )
    op.drop_index(
        "ix_user_schedule_items_user_id_scheduled_date",
        table_name="user_schedule_items",
    )
    op.drop_table("user_schedule_items")
