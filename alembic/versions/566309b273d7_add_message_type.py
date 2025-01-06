"""add message type

Revision ID: 566309b273d7
Revises: e233804adc91
Create Date: 2024-12-21 18:02:16.765201

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '566309b273d7'
down_revision: Union[str, None] = 'e233804adc91'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('message', sa.Column('message_type', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('message', 'message_type')
