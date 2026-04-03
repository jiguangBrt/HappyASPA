"""merge db heads

Revision ID: 2ef8029c5dc5
Revises: 074f10ff2d88, 8530d4d43976
Create Date: 2026-04-02 21:53:54.446497

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2ef8029c5dc5'
down_revision = ('074f10ff2d88', '8530d4d43976')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
