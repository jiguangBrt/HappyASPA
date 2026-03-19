"""Merge database branches

Revision ID: a4003bbafb0f
Revises: 316b2cf72771, 44d725adc086
Create Date: 2026-03-13 18:13:30.386469

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "a4003bbafb0f"
down_revision = ("316b2cf72771", "44d725adc086")
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
