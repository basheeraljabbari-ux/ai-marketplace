"""add category_suggestions to listing_ai_metadata

Revision ID: 0004
Revises: 0003
Create Date: 2026-07-28
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql as pg

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # nullable: الصفوف الموجودة تبقى NULL — الاقتراحات تنكتب فقط للإعلانات الجديدة
    # اللي يعالجها الـ AI worker بعد هذي الهجرة.
    op.add_column(
        "listing_ai_metadata",
        sa.Column("category_suggestions", pg.JSONB, nullable=True),
    )


def downgrade() -> None:
    op.drop_column("listing_ai_metadata", "category_suggestions")
