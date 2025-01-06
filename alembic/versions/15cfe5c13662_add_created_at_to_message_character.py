"""add_created_at_to_message_character

Revision ID: 15cfe5c13662
Revises: 0997887ce01c
Create Date: 2024-12-22 10:20:26.725771

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '15cfe5c13662'
down_revision: Union[str, None] = '0997887ce01c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Add created_at column
    op.add_column('message_character', 
        sa.Column('created_at', 
                 sa.DateTime(), 
                 nullable=False,
                 server_default=sa.text('NOW()')
        )
    )

    # Update existing records to match their message's wen_posted
    conn = op.get_bind()
    conn.execute(
        sa.text("""
            UPDATE message_character mc
            SET created_at = m.wen_posted
            FROM message m
            WHERE mc.message_id = m.id
        """)
    )

def downgrade():
    # Remove created_at column
    op.drop_column('message_character', 'created_at')