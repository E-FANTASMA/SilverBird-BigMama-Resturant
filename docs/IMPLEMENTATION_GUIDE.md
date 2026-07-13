# Project X Implementation Guide

This document explains what each file does and what the current code is responsible for.

## Root files

### `README.md`
Project overview and local run instructions.

### `.env.example`
Template for required environment variables.

### `requirements.txt`
Dependency list for the backend.

### `alembic.ini`
Alembic configuration file that points migration commands at the application database URL.

## App bootstrap

### `app/main.py`
Creates the FastAPI app, registers middleware and exception handlers, mounts API routes, and exposes the `/health` endpoint.

## Core modules

### `app/core/config.py`
Loads settings for database access, JWT, Paystack, Supabase, delivery pricing, email, and SMS.

### `app/core/constants.py`
Stores small shared constants such as allowed image extensions.

### `app/core/security.py`
Handles password hashing and JWT creation/decoding.

### `app/core/exceptions.py`
Defines reusable application exceptions.

### `app/core/exception_handlers.py`
Converts application exceptions into HTTP responses.

## Domain

### `app/domain/enums.py`
Contains the main business enums used across models, services, and schemas.

## Database foundation

### `app/infrastructure/database/base.py`
Defines the SQLAlchemy base class and reusable UUID, timestamp, and soft-delete mixins.

### `app/infrastructure/database/session.py`
Creates the database engine and request-scoped session dependency.

## Database setup and migrations

### `alembic/env.py`
Loads the application settings and SQLAlchemy metadata so Alembic can create and apply migrations against Supabase Postgres.

### `alembic/versions/0001_initial_schema.py`
Initial migration that creates the core enums and tables for users, catalog, carts, orders, payments, deliveries, and notifications.

### `app/scripts/init_db.py`
Bootstrap script that can create all SQLAlchemy tables directly and seed the default roles when you want a quick first-time setup.

## Database models

### `app/infrastructure/database/models/role.py`
Role table for `CUSTOMER`, `ADMIN`, and `DELIVERY_PERSONNEL`.

### `app/infrastructure/database/models/user.py`
User table for customers, admins, and riders.

### `app/infrastructure/database/models/token.py`
Refresh token and password reset token persistence models.

### `app/infrastructure/database/models/category.py`
Food category model.

### `app/infrastructure/database/models/food.py`
Menu item model, including image metadata and availability.

### `app/infrastructure/database/models/cart.py`
Cart and cart-item models.

### `app/infrastructure/database/models/order.py`
Order and order-item snapshot models.

### `app/infrastructure/database/models/payment.py`
Payment and webhook-event models.

### `app/infrastructure/database/models/address.py`
Customer delivery address model.

### `app/infrastructure/database/models/delivery.py`
Assigned delivery model for riders.

### `app/infrastructure/database/models/notification.py`
In-app notification records and outbound email/SMS delivery tracking.

## Repositories

### `app/infrastructure/database/repositories/base.py`
Generic repository helper for CRUD-style operations.

### Specific repositories
User, role, category, food, cart, order, payment, address, delivery, and notification repositories wrap database querying for their modules.

## Services

### `app/application/services/auth_service.py`
Implements signup, login, refresh, and token issuance flow.

### `app/application/services/user_service.py`
Handles profile retrieval and updates.

### `app/application/services/category_service.py`
Handles category creation, listing, and updates.

### `app/application/services/food_service.py`
Handles food listing, retrieval, creation, and updates.

### `app/application/services/cart_service.py`
Handles cart retrieval and cart-item mutation.

### `app/application/services/pricing_service.py`
Calculates delivery distance and distance-based fee.

### `app/application/services/order_service.py`
Creates unpaid orders from cart contents and clears the cart after order creation.

### `app/application/services/payment_service.py`
Creates payment attempts and updates payment/order state during verification.

### `app/application/services/delivery_service.py`
Assigns riders and allows riders to update delivery status.

### `app/application/services/notification_service.py`
Creates in-app notifications and email/SMS delivery tracking rows.

### `app/application/services/report_service.py`
Builds simple admin dashboard metrics.

## Schemas

### `app/schemas/*.py`
Each schema file separates API contracts from database models:

- `auth.py`: auth requests and responses
- `user.py`: profile schemas
- `category.py`: category schemas
- `food.py`: food schemas
- `cart.py`: cart schemas
- `order.py`: order schemas
- `payment.py`: payment schemas
- `address.py`: delivery address schemas
- `delivery.py`: delivery schemas
- `notification.py`: notification schemas
- `common.py`: shared base schema classes

## Dependencies

### `app/dependencies/auth.py`
Decodes the access token, loads the authenticated user, and enforces RBAC.

### `app/dependencies/services.py`
Creates service instances for FastAPI dependency injection.

## Routers

### `app/api/v1/router.py`
Composes all versioned API routers.

### `app/api/v1/routers/*`
Each file exposes a focused endpoint group:

- `auth.py`: signup, login, refresh, logout placeholder
- `profile.py`: profile read/update
- `categories.py`: category endpoints
- `foods.py`: food endpoints
- `cart.py`: cart endpoints
- `orders.py`: order endpoints
- `payments.py`: Paystack initialize/verify endpoints
- `addresses.py`: delivery address endpoints
- `notifications.py`: notification endpoints
- `admin_dashboard.py`: dashboard metrics
- `admin_orders.py`: admin order lookup and rider assignment
- `admin_users.py`: admin user list
- `admin_reports.py`: admin reports
- `delivery_orders.py`: rider delivery endpoints

## Middleware

### `app/middleware/request_id.py`
Attaches a request ID to requests and responses for traceability.

## Tests

### `tests/test_health.py`
Simple smoke test proving that the app boots and the health endpoint responds.

## Current implementation status

The code currently includes:

- layered FastAPI project structure
- SQLAlchemy models for the main business entities
- repository abstractions
- service layer for auth, catalog, cart, orders, payments, delivery, notifications, and reporting
- unpaid-first order creation flow
- distance-based delivery fee calculation
- role-protected routes
- in-app, email, and SMS notification tracking

The next production-hardening steps are:

- wire live Paystack API calls and webhook verification
- add Supabase Storage image upload and deletion adapter
- add email and SMS provider clients
- expand tests and pagination/filtering
