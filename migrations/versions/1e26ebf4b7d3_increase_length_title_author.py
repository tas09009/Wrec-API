"""increase length: title & author

Revision ID: 1e26ebf4b7d3
Revises: 8910dc11c870
Create Date: 2023-06-29 12:41:57.768846

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1e26ebf4b7d3'
down_revision = '8910dc11c870'
branch_labels = None
depends_on = None


def upgrade():
    # Alter the column type from String(128) to String()
    with op.batch_alter_table('books') as batch_op:
        batch_op.alter_column('title', existing_type=sa.String(length=128), type_=sa.String())
        batch_op.alter_column('author', existing_type=sa.String(length=128), type_=sa.String())

def downgrade():
    # If you need to rollback the migration, you can define a downgrade function
    with op.batch_alter_table('books') as batch_op:
        batch_op.alter_column('author', existing_type=sa.String(), type_=sa.String(length=128))
        batch_op.alter_column('title', existing_type=sa.String(), type_=sa.String(length=128))
