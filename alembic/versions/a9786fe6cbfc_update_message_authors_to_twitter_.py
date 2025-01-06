"""Update message authors to twitter handles

Revision ID: a9786fe6cbfc
Revises: adfded2ef67e
Create Date: 2024-11-30 18:02:36.345457

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a9786fe6cbfc"
down_revision: Union[str, None] = "adfded2ef67e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Update the author field where it is exactly 'Sia' or 'KIKI'
    op.execute(
        """
        UPDATE message
        SET author = 'sia_really'
        WHERE author = 'Sia'
        """
    )
    op.execute(
        """
        UPDATE message
        SET author = 'KikiTheProphecy'
        WHERE author = 'KIKI'
        """
    )


def downgrade():
    # Optionally, reverse the changes
    op.execute(
        """
        UPDATE message
        SET author = 'Sia'
        WHERE author = 'sia_really'
        """
    )
    op.execute(
        """
        UPDATE message
        SET author = 'KIKI'
        WHERE author = 'KikiTheProphecy'
        """
    )
