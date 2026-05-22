"""add flags column to books

Revision ID: 20260522_add_flags
Revises: 20260522_add_isbn
Create Date: 2026-05-22 13:35:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20260522_add_flags'
down_revision = '20260522_add_isbn'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    exists = conn.execute(sa.text("SELECT 1 FROM information_schema.columns WHERE table_name='books' AND column_name='flags'")).fetchone()
    if not exists:
        op.add_column('books', sa.Column('flags', sa.Integer(), server_default=sa.text('1'), nullable=False))


def downgrade():
    conn = op.get_bind()
    exists = conn.execute(sa.text("SELECT 1 FROM information_schema.columns WHERE table_name='books' AND column_name='flags'")).fetchone()
    if exists:
        op.drop_column('books', 'flags')
