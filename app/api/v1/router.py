from fastapi import APIRouter

from app.api.v1.routers import (
    addresses,
    admin_dashboard,
    admin_orders,
    admin_reports,
    admin_users,
    auth,
    cart,
    categories,
    delivery_orders,
    foods,
    notifications,
    orders,
    payments,
    profile,
)

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(profile.router, prefix="/profile", tags=["Profile"])
api_router.include_router(categories.router, prefix="/categories", tags=["Categories"])
api_router.include_router(foods.router, prefix="/foods", tags=["Foods"])
api_router.include_router(cart.router, prefix="/cart", tags=["Cart"])
api_router.include_router(orders.router, prefix="/orders", tags=["Orders"])
api_router.include_router(payments.router, prefix="/payments", tags=["Payments"])
api_router.include_router(addresses.router, prefix="/addresses", tags=["Addresses"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
api_router.include_router(admin_dashboard.router, prefix="/admin/dashboard", tags=["Admin Dashboard"])
api_router.include_router(admin_orders.router, prefix="/admin/orders", tags=["Admin Orders"])
api_router.include_router(admin_users.router, prefix="/admin/users", tags=["Admin Users"])
api_router.include_router(admin_reports.router, prefix="/admin/reports", tags=["Admin Reports"])
api_router.include_router(delivery_orders.router, prefix="/delivery/orders", tags=["Delivery Orders"])
