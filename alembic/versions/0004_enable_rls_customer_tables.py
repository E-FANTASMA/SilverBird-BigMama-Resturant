"""enable row level security on customer-facing tables

Revision ID: 0004_enable_rls_customer_tables
Revises: 0003_order_checkout_fields
Create Date: 2026-08-17 10:30:00

This migration enables RLS on customer-facing tables and adds starter
policies that rely on request-scoped Postgres settings:

- app.current_user_id
- app.current_user_role

The current backend still connects with a shared server-side database role,
so these policies are primarily groundwork for safer rollout and do not force
RLS on the application role.
"""

from alembic import op


revision = "0004_enable_rls_customer_tables"
down_revision = "0003_order_checkout_fields"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        alter table delivery_addresses enable row level security;
        alter table carts enable row level security;
        alter table cart_items enable row level security;
        alter table orders enable row level security;
        alter table order_items enable row level security;
        alter table payments enable row level security;
        alter table notifications enable row level security;
        alter table notification_deliveries enable row level security;
        alter table deliveries enable row level security;
        """
    )

    op.execute(
        """
        create policy delivery_addresses_owner_access on delivery_addresses
        using (
            user_id = nullif(current_setting('app.current_user_id', true), '')::uuid
            or current_setting('app.current_user_role', true) = 'ADMIN'
        )
        with check (
            user_id = nullif(current_setting('app.current_user_id', true), '')::uuid
            or current_setting('app.current_user_role', true) = 'ADMIN'
        );

        create policy carts_owner_access on carts
        using (
            user_id = nullif(current_setting('app.current_user_id', true), '')::uuid
            or current_setting('app.current_user_role', true) = 'ADMIN'
        )
        with check (
            user_id = nullif(current_setting('app.current_user_id', true), '')::uuid
            or current_setting('app.current_user_role', true) = 'ADMIN'
        );

        create policy cart_items_owner_access on cart_items
        using (
            exists (
                select 1
                from carts
                where carts.id = cart_items.cart_id
                and (
                    carts.user_id = nullif(current_setting('app.current_user_id', true), '')::uuid
                    or current_setting('app.current_user_role', true) = 'ADMIN'
                )
            )
        )
        with check (
            exists (
                select 1
                from carts
                where carts.id = cart_items.cart_id
                and (
                    carts.user_id = nullif(current_setting('app.current_user_id', true), '')::uuid
                    or current_setting('app.current_user_role', true) = 'ADMIN'
                )
            )
        );

        create policy orders_owner_access on orders
        using (
            user_id = nullif(current_setting('app.current_user_id', true), '')::uuid
            or current_setting('app.current_user_role', true) = 'ADMIN'
        )
        with check (
            user_id = nullif(current_setting('app.current_user_id', true), '')::uuid
            or current_setting('app.current_user_role', true) = 'ADMIN'
        );

        create policy order_items_owner_access on order_items
        using (
            exists (
                select 1
                from orders
                where orders.id = order_items.order_id
                and (
                    orders.user_id = nullif(current_setting('app.current_user_id', true), '')::uuid
                    or current_setting('app.current_user_role', true) = 'ADMIN'
                )
            )
        )
        with check (
            exists (
                select 1
                from orders
                where orders.id = order_items.order_id
                and (
                    orders.user_id = nullif(current_setting('app.current_user_id', true), '')::uuid
                    or current_setting('app.current_user_role', true) = 'ADMIN'
                )
            )
        );

        create policy payments_owner_access on payments
        using (
            exists (
                select 1
                from orders
                where orders.id = payments.order_id
                and (
                    orders.user_id = nullif(current_setting('app.current_user_id', true), '')::uuid
                    or current_setting('app.current_user_role', true) = 'ADMIN'
                )
            )
        )
        with check (
            exists (
                select 1
                from orders
                where orders.id = payments.order_id
                and (
                    orders.user_id = nullif(current_setting('app.current_user_id', true), '')::uuid
                    or current_setting('app.current_user_role', true) = 'ADMIN'
                )
            )
        );

        create policy notifications_owner_access on notifications
        using (
            user_id = nullif(current_setting('app.current_user_id', true), '')::uuid
            or current_setting('app.current_user_role', true) = 'ADMIN'
        )
        with check (
            user_id = nullif(current_setting('app.current_user_id', true), '')::uuid
            or current_setting('app.current_user_role', true) = 'ADMIN'
        );

        create policy notification_deliveries_owner_access on notification_deliveries
        using (
            exists (
                select 1
                from notifications
                where notifications.id = notification_deliveries.notification_id
                and (
                    notifications.user_id = nullif(current_setting('app.current_user_id', true), '')::uuid
                    or current_setting('app.current_user_role', true) = 'ADMIN'
                )
            )
        )
        with check (
            exists (
                select 1
                from notifications
                where notifications.id = notification_deliveries.notification_id
                and (
                    notifications.user_id = nullif(current_setting('app.current_user_id', true), '')::uuid
                    or current_setting('app.current_user_role', true) = 'ADMIN'
                )
            )
        );

        create policy deliveries_customer_or_rider_access on deliveries
        using (
            delivery_personnel_id = nullif(current_setting('app.current_user_id', true), '')::uuid
            or current_setting('app.current_user_role', true) = 'ADMIN'
            or exists (
                select 1
                from orders
                where orders.id = deliveries.order_id
                and orders.user_id = nullif(current_setting('app.current_user_id', true), '')::uuid
            )
        )
        with check (
            delivery_personnel_id = nullif(current_setting('app.current_user_id', true), '')::uuid
            or current_setting('app.current_user_role', true) = 'ADMIN'
        );
        """
    )


def downgrade() -> None:
    op.execute(
        """
        drop policy if exists deliveries_customer_or_rider_access on deliveries;
        drop policy if exists notification_deliveries_owner_access on notification_deliveries;
        drop policy if exists notifications_owner_access on notifications;
        drop policy if exists payments_owner_access on payments;
        drop policy if exists order_items_owner_access on order_items;
        drop policy if exists orders_owner_access on orders;
        drop policy if exists cart_items_owner_access on cart_items;
        drop policy if exists carts_owner_access on carts;
        drop policy if exists delivery_addresses_owner_access on delivery_addresses;

        alter table deliveries disable row level security;
        alter table notification_deliveries disable row level security;
        alter table notifications disable row level security;
        alter table payments disable row level security;
        alter table order_items disable row level security;
        alter table orders disable row level security;
        alter table cart_items disable row level security;
        alter table carts disable row level security;
        alter table delivery_addresses disable row level security;
        """
    )
