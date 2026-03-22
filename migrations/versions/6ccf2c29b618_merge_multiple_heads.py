"""merge multiple heads

Revision ID: 6ccf2c29b618
Revises: 05b649573024, c85c65673c69
Create Date: 2026-03-19 20:28:28.316589

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "6ccf2c29b618"
down_revision = ("05b649573024", "c85c65673c69")
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
