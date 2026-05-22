"""add isbn column to books

Revision ID: 20260522_add_isbn
Revises: 0cbf2c05458b
Create Date: 2026-05-22 13:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20260522_add_isbn'
down_revision = '0cbf2c05458b'
branch_labels = None
depends_on = None


def upgrade():
    # Add isbn column if it does not exist
    conn = op.get_bind()
    # Postgres: check column existence
    exists = conn.execute(sa.text("SELECT 1 FROM information_schema.columns WHERE table_name='books' AND column_name='isbn'")).fetchone()
    if not exists:
        op.add_column('books', sa.Column('isbn', sa.Text(), server_default=sa.text("''"), nullable=True))


def downgrade():
    conn = op.get_bind()
    exists = conn.execute(sa.text("SELECT 1 FROM information_schema.columns WHERE table_name='books' AND column_name='isbn'")).fetchone()
    if exists:
        op.drop_column('books', 'isbn')
