"""add_password_hash

Revision ID: e8d3e7a38086
Revises: 1e26ebf4b7d3
Create Date: 2023-09-27 17:39:23.940142

"""
from alembic import op
from sqlalchemy import table, column
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e8d3e7a38086'
down_revision = '1e26ebf4b7d3'
branch_labels = None
depends_on = None


def upgrade():
    """
    Add password_hash attribute as nullable.
    Set default value of 'password_default'
    """
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('password_hash', sa.String(length=128), nullable=True))
    conn = op.get_bind()
    users = table('users', column('password_hash', sa.String(length=128)))
    stmt = (
        users.update().
        where(users.c.password_hash == None).
        values(password_hash='password_default')
    )
    conn.execute(stmt)

def downgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('password_hash')
