"""merge different migrade db branch

Revision ID: 1aff063331b4
Revises: 316b2cf72771, 44d725adc086
Create Date: 2026-03-15 00:31:14.291485

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1aff063331b4'
down_revision = ('316b2cf72771', '44d725adc086')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
