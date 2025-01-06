"""Change created_at to TIMESTAMP in knowledge_google_news_search

Revision ID: e233804adc91
Revises: a9786fe6cbfc
Create Date: 2024-12-03 08:59:41.188272

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e233804adc91"
down_revision: Union[str, None] = "a9786fe6cbfc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Change the column type to TIMESTAMP
    op.alter_column(
        "knowledge_google_news_search",
        "created_at",
        existing_type=sa.String(),  # or sa.VARCHAR() if that's what it was
        type_=sa.TIMESTAMP(),
        postgresql_using="created_at::timestamp",
    )


def downgrade():
    # Revert the column type back to STRING
    op.alter_column(
        "knowledge_google_news_search",
        "created_at",
        existing_type=sa.TIMESTAMP(),
        type_=sa.String(),
    )  # or sa.VARCHAR() if that's what it was
