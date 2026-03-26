"""merge conflicting heads

Revision ID: c43e16d45f52
Revises: 01f67ceafa1c, 370d84537341
Create Date: 2026-03-26 17:31:46.600803

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c43e16d45f52'
down_revision = ('01f67ceafa1c', '370d84537341')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
