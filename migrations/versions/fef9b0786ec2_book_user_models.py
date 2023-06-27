"""Book + User models

Revision ID: fef9b0786ec2
Revises: f36bc9474f9a
Create Date: 2023-04-13 11:45:57.642215

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fef9b0786ec2'
down_revision = 'f36bc9474f9a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('books',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=128), nullable=True),
    sa.Column('author', sa.String(length=128), nullable=True, unique=False),
    sa.Column('dewey_decimal', sa.Integer(), nullable=True),
    sa.Column('isbn', sa.String(length=16), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=128), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    # op.drop_table('user_book')
    op.drop_table('users')
    op.drop_table('books')

    op.execute("SELECT setval('users_id_seq', 1, false);")
    op.execute("SELECT setval('books_id_seq', 1, false);")
    # ### end Alembic commands ###