"""merge multiple heads

Revision ID: 80912fcd13bd
Revises: 065dab6ae8d0, 18b75ff8509d
Create Date: 2026-04-01 21:23:38.383539

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '80912fcd13bd'
down_revision = ('065dab6ae8d0', '18b75ff8509d')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
