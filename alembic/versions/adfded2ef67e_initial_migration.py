"""Initial migration

Revision ID: adfded2ef67e
Revises:
Create Date: 2024-11-29 12:52:17.957076

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "adfded2ef67e"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Create a new temporary table with the desired schema
    op.create_table(
        "message_temp",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("conversation_id", sa.String()),
        sa.Column("character", sa.String()),
        sa.Column("platform", sa.String(), nullable=False),
        sa.Column("author", sa.String(), nullable=False),
        sa.Column("content", sa.String(), nullable=False),
        sa.Column("response_to", sa.String()),
        sa.Column("wen_posted", sa.DateTime(), default=sa.func.now()),
        sa.Column("original_data", sa.JSON()),
        sa.Column("flagged", sa.Boolean(), nullable=True),
        # Changed to Boolean
        sa.Column("message_metadata", sa.JSON()),
    )

    # Copy data from the old table to the new table
    op.execute(
        """
        INSERT INTO message_temp (id, conversation_id, character, platform, author, content, response_to, wen_posted, original_data, flagged, message_metadata)
        SELECT id, conversation_id, character, platform, author, content, response_to, wen_posted, original_data, False, message_metadata
        FROM message
    """
    )

    # Drop the old table
    op.drop_table("message")

    # Rename the new table to the original table name
    op.rename_table("message_temp", "message")


def downgrade():
    # Reverse the process for downgrade
    op.create_table(
        "message_temp",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("conversation_id", sa.String()),
        sa.Column("character", sa.String()),
        sa.Column("platform", sa.String(), nullable=False),
        sa.Column("author", sa.String(), nullable=False),
        sa.Column("content", sa.String(), nullable=False),
        sa.Column("response_to", sa.String()),
        sa.Column("wen_posted", sa.DateTime(), default=sa.func.now()),
        sa.Column("original_data", sa.JSON()),
        sa.Column("flagged", sa.String(), nullable=True),
        # Revert to original type
        sa.Column("message_metadata", sa.JSON()),
    )

    op.execute(
        """
        INSERT INTO message_temp (id, conversation_id, character, platform, author, content, response_to, wen_posted, original_data, flagged, message_metadata)
        SELECT id, conversation_id, character, platform, author, content, response_to, wen_posted, original_data, flagged, message_metadata
        FROM message
    """
    )

    op.drop_table("message")
    op.rename_table("message_temp", "message")
