"""merge migration heads

Revision ID: 06f1b19cf838
Revises: 65b01b6f68cd, 7a8c2ad446e5
Create Date: 2026-03-27 14:28:19.673311

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '06f1b19cf838'
down_revision = ('65b01b6f68cd', '7a8c2ad446e5')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
