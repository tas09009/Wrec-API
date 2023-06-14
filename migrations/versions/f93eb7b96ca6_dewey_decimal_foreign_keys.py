"""dewey_decimal_foreign_keys

Revision ID: f93eb7b96ca6
Revises: bf3b1e743b3c
Create Date: 2023-06-14 17:40:21.751986

"""
from alembic import op
import sqlalchemy as sa

from db import db
from models import DeweyLevel_2, DeweyLevel_3


# revision identifiers, used by Alembic.
revision = 'f93eb7b96ca6'
down_revision = 'bf3b1e743b3c'
branch_labels = None
depends_on = None


def upgrade():
    """
    Populate the foreign key values:
    DeweyLevel_3.level_2_id: Level 3 (Thousand rows):
    DeweyLevel_2.level_1_id: Level 2 (Hundred rows):
    """

    start = 1
    stop = 10
    hundred_category_id = 1
    while hundred_category_id <= 100:
        thousand_categories_subgroup = DeweyLevel_3.query.filter(DeweyLevel_3.id.between(start,stop)).all()
        for category in thousand_categories_subgroup:
            category.level_2_id = hundred_category_id
            db.session.add(category)

        start += 10
        stop += 10
        hundred_category_id += 1


    start = 1
    stop = 10
    ten_category_id = 1
    while ten_category_id <= 10:
        hundred_categories_subgroup = DeweyLevel_2.query.filter(DeweyLevel_2.id.between(start,stop)).all()
        for category in hundred_categories_subgroup:
            category.level_1_id = ten_category_id
            db.session.add(category)

        start += 10
        stop += 10
        ten_category_id += 1


    db.session.commit()



def downgrade():
    pass
