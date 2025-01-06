"""add message indexes

Revision ID: ac438a8b7806
Revises: 15cfe5c13662
Create Date: 2024-12-26 09:11:16.302910

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ac438a8b7806'
down_revision: Union[str, None] = '15cfe5c13662'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create indexes for better query performance
    op.create_index('idx_message_author', 'message', ['author'])
    op.create_index('idx_message_response_to', 'message', ['response_to'])


def downgrade() -> None:
    # Remove indexes
    op.drop_index('idx_message_author', table_name='message')
    op.drop_index('idx_message_response_to', table_name='message')