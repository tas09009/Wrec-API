"""all_tables_API

Revision ID: d08c44624786
Revises: 8cbe23b4c39e
Create Date: 2021-09-16 17:37:58.421249

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "d08c44624786"
down_revision = "8cbe23b4c39e"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "ten_categories_ddc",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("call_number", sa.String(), nullable=True),
        sa.Column("classification", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=64), nullable=True),
        sa.Column("username", sa.String(length=64), nullable=True),
        sa.Column("password_hash", sa.String(length=128), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_table(
        "hundred_categories_ddc",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("call_number", sa.String(), nullable=True),
        sa.Column("classification", sa.String(), nullable=True),
        sa.Column("tens_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["tens_id"],
            ["ten_categories_ddc.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "thousand_categories_ddc",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("call_number", sa.String(), nullable=True),
        sa.Column("classification", sa.String(), nullable=True),
        sa.Column("hundreds_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["hundreds_id"],
            ["hundred_categories_ddc.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "books",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("classify_ddc", sa.String(), nullable=True),
        sa.Column("classify_category", sa.String(), nullable=True),
        sa.Column("classify_ten_id", sa.Integer(), nullable=True),
        sa.Column("classify_hundred_id", sa.Integer(), nullable=True),
        sa.Column("classify_thousand_id", sa.Integer(), nullable=True),
        sa.Column("title", sa.String(), nullable=True),
        sa.Column("author", sa.String(), nullable=True),
        sa.Column("isbn", sa.String(), nullable=True),
        sa.Column("isbn13", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ["classify_hundred_id"],
            ["hundred_categories_ddc.id"],
        ),
        sa.ForeignKeyConstraint(
            ["classify_ten_id"],
            ["ten_categories_ddc.id"],
        ),
        sa.ForeignKeyConstraint(
            ["classify_thousand_id"],
            ["thousand_categories_ddc.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "bookshelf",
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("book_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["book_id"],
            ["books.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("bookshelf")
    op.drop_table("books")
    op.drop_table("thousand_categories_ddc")
    op.drop_table("hundred_categories_ddc")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
    op.drop_table("ten_categories_ddc")
    # ### end Alembic commands ###
