"""add_message_character_table

Revision ID: 0997887ce01c
Revises: 566309b273d7
Create Date: 2024-12-22 10:02:33.486428

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision: str = '0997887ce01c'
down_revision: Union[str, None] = '566309b273d7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Create new table
    op.create_table(
        'message_character',
        sa.Column('message_id', sa.String(), nullable=False),
        sa.Column('character_name', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['message_id'], ['message.id'], ),
        sa.PrimaryKeyConstraint('message_id')
    )

    # Migrate existing data
    conn = op.get_bind()
    
    # Get all messages with characters
    messages = conn.execute(
        text('SELECT id, character FROM message WHERE character IS NOT NULL')
    ).fetchall()
    
    # Insert into new table
    for message_id, character in messages:
        if character:
            conn.execute(
                text('INSERT INTO message_character (message_id, character_name) VALUES (:mid, :char)'),
                {'mid': message_id, 'char': character}
            )
    
    # Remove old column
    op.drop_column('message', 'character')

def downgrade():
    # Add back the character column
    op.add_column('message', sa.Column('character', sa.String()))
    
    # Migrate data back
    conn = op.get_bind()
    
    # Get all message_character relationships
    chars = conn.execute(
        text('SELECT message_id, character_name FROM message_character')
    ).fetchall()
    
    # Update messages
    for message_id, character_name in chars:
        conn.execute(
            text('UPDATE message SET character = :char WHERE id = :mid'),
            {'char': character_name, 'mid': message_id}
        )
    
    # Drop the new table
    op.drop_table('message_character')