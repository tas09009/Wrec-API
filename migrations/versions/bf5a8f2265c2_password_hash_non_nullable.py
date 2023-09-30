"""password_hash_non_nullable

Revision ID: bf5a8f2265c2
Revises: e8d3e7a38086
Create Date: 2023-09-28 15:33:46.820236

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bf5a8f2265c2'
down_revision = 'e8d3e7a38086'
branch_labels = None
depends_on = None


def upgrade():
    """
    Make password_hash non-nullable
    """
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('password_hash', existing_type=sa.String(length=128), nullable=False)

def downgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('password_hash', existing_type=sa.String(length=128), nullable=True)



