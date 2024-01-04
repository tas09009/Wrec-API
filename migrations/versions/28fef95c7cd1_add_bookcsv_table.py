"""add bookcsv table

Revision ID: 28fef95c7cd1
Revises: bf5a8f2265c2
Create Date: 2024-01-02 21:16:04.408402

"""
from alembic import op
import sqlalchemy as sa


revision = "28fef95c7cd1"
down_revision = "bf5a8f2265c2"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "book_csv",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("filename", sa.String(), nullable=False),
        sa.Column("s3_url", sa.String(), nullable=True),
        sa.Column("uploaded_at", sa.DateTime(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("book_csv")
