"""Import Dewey Levels

Revision ID: f36bc9474f9a
Revises: 80b0ea80d3c8
Create Date: 2023-04-11 14:37:09.442839

"""
import csv
import sqlalchemy as sa
from sqlalchemy import text
from alembic import op
from models import DeweyDecimalSystem, DeweyLevel_1, DeweyLevel_2, DeweyLevel_3
from db import db


# revision identifiers, used by Alembic.
revision = 'f36bc9474f9a'
down_revision = '80b0ea80d3c8'
branch_labels = None
depends_on = None


def upgrade():

    # Create a new DeweyDecimalSystem record for level 1
    with op.batch_alter_table('dewey_decimal_system', schema='public') as batch_op:
        dewey_system_1 = DeweyDecimalSystem()
        db.session.add(dewey_system_1)
        db.session.commit()

    # Populate Level 1 table from csv file
    with op.batch_alter_table('dewey_level_1', schema='public') as batch_op:
        with open('dewey_levels/level_1.csv', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                dewey_level = DeweyLevel_1(
                    code=int(row['code']),
                    description=row['description'],
                    value=4,
                    dewey_decimal_system_id=dewey_system_1.id
                )
                db.session.add(dewey_level)
                db.session.commit()

    # Create a new DeweyDecimalSystem record for level 2
    with op.batch_alter_table('dewey_decimal_system', schema='public') as batch_op:
        dewey_system_2 = DeweyDecimalSystem()
        db.session.add(dewey_system_2)
        db.session.commit()

    # Populate Level 2 table from csv file
    with op.batch_alter_table('dewey_level_2', schema='public') as batch_op:
        with open('dewey_levels/level_2.csv', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                dewey_level = DeweyLevel_2(
                    code=int(row['code']),
                    description=row['description'],
                    value=3,
                    dewey_decimal_system_id=dewey_system_2.id
                )
                db.session.add(dewey_level)
                db.session.commit()

    # Create a new DeweyDecimalSystem record for level 4
    with op.batch_alter_table('dewey_decimal_system', schema='public') as batch_op:
        dewey_system_3 = DeweyDecimalSystem()
        db.session.add(dewey_system_3)
        db.session.commit()

    # Populate Level 3 table from csv file
    with op.batch_alter_table('dewey_level_3', schema='public') as batch_op:
        with open('dewey_levels/level_3.csv', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                dewey_level = DeweyLevel_3(
                    code=int(row['code']),
                    description=row['description'],
                    value=2,
                    dewey_decimal_system_id=dewey_system_3.id
                )
                db.session.add(dewey_level)
                db.session.commit()


def downgrade():
    conn = op.get_bind()

    # Delete all rows from the three dewey level tables
    conn.execute(sa.text("DELETE FROM dewey_level_3"))
    conn.execute(sa.text("DELETE FROM dewey_level_2"))
    conn.execute(sa.text("DELETE FROM dewey_level_1"))

    # Delete all rows from dewey_decimal_system table
    conn.execute(sa.text("DELETE FROM dewey_decimal_system"))
