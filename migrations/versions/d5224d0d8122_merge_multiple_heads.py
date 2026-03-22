"""merge multiple heads

Revision ID: d5224d0d8122
Revises: 49cfded8f5eb, 6ccf2c29b618
Create Date: 2026-03-20 08:29:54.519519

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd5224d0d8122'
down_revision = ('49cfded8f5eb', '6ccf2c29b618')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
