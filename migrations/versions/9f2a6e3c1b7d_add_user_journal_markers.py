"""add user journal markers

Revision ID: 9f2a6e3c1b7d
Revises: 65b01b6f68cd
Create Date: 2026-03-27 16:45:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9f2a6e3c1b7d'
down_revision = '65b01b6f68cd'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'user_journal_markers',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('kind', sa.String(length=30), nullable=True),
        sa.Column('value', sa.Float(), nullable=True),
        sa.Column('unit', sa.String(length=20), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('color', sa.String(length=20), nullable=True),
        sa.Column('event_date', sa.Date(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
    )
    op.create_index(
        'ix_user_journal_markers_event_date',
        'user_journal_markers',
        ['event_date'],
        unique=False,
    )


def downgrade():
    op.drop_index('ix_user_journal_markers_event_date', table_name='user_journal_markers')
    op.drop_table('user_journal_markers')
