"""add_invite_code

Revision ID: cbbdcec7114c
Revises: f4e8a1b9c0d2
Create Date: 2026-04-07 17:44:58.144149

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cbbdcec7114c'
down_revision = 'f4e8a1b9c0d2'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = {column["name"] for column in inspector.get_columns("teams")}
    indexes = {index["name"] for index in inspector.get_indexes("teams")}
    invite_index_name = "ix_teams_invite_code"

    with op.batch_alter_table("teams", schema=None) as batch_op:
        if "invite_code" not in columns:
            batch_op.add_column(sa.Column("invite_code", sa.String(length=10), nullable=True))
        if invite_index_name not in indexes:
            batch_op.create_index(batch_op.f(invite_index_name), ["invite_code"], unique=True)


def downgrade():
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = {column["name"] for column in inspector.get_columns("teams")}
    indexes = {index["name"] for index in inspector.get_indexes("teams")}
    invite_index_name = "ix_teams_invite_code"

    with op.batch_alter_table("teams", schema=None) as batch_op:
        if invite_index_name in indexes:
            batch_op.drop_index(batch_op.f(invite_index_name))
        if "invite_code" in columns:
            batch_op.drop_column("invite_code")
