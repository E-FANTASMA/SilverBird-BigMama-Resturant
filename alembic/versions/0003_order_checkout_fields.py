"""add order checkout fields

Revision ID: 0003_order_checkout_fields
Revises: 0002_auth_phone_unique
Create Date: 2026-07-16 15:30:00
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision = "0003_order_checkout_fields"
down_revision = "0002_auth_phone_unique"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("orders", sa.Column("delivery_address_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column("orders", sa.Column("table_number", sa.String(length=30), nullable=True))
    op.create_foreign_key("fk_orders_delivery_address_id", "orders", "delivery_addresses", ["delivery_address_id"], ["id"])
    op.create_index("ix_orders_delivery_address_id", "orders", ["delivery_address_id"])


def downgrade() -> None:
    op.drop_index("ix_orders_delivery_address_id", table_name="orders")
    op.drop_constraint("fk_orders_delivery_address_id", "orders", type_="foreignkey")
    op.drop_column("orders", "table_number")
    op.drop_column("orders", "delivery_address_id")
