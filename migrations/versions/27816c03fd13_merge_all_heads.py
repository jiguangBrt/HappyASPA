"""merge all heads

Revision ID: 27816c03fd13
Revises: 440daf34526f, 76599cff4d57, e91837fb18ec
Create Date: 2026-04-01 09:31:45.916910

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '27816c03fd13'
down_revision = ('440daf34526f', '76599cff4d57', 'e91837fb18ec')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
