"""merge multiple heads

Revision ID: a872908ff3fe
Revises: 074f10ff2d88, 8530d4d43976
Create Date: 2026-04-02 20:39:16.507362

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a872908ff3fe'
down_revision = ('074f10ff2d88', '8530d4d43976')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
