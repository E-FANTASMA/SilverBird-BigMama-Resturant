"""add phone uniqueness for users

Revision ID: 0002_auth_phone_unique
Revises: 0001_initial_schema
Create Date: 2026-07-14 10:30:00
"""

from alembic import op


revision = "0002_auth_phone_unique"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_unique_constraint("uq_users_phone", "users", ["phone"])


def downgrade() -> None:
    op.drop_constraint("uq_users_phone", "users", type_="unique")
