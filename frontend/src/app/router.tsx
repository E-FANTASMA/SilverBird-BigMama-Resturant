import { createBrowserRouter, Navigate, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "@/auth/auth-store";
import { AdminShell, CustomerShell, DeliveryShell, PublicMenuShell } from "@/components/layout";
import {
  AdminDashboardPage,
  AdminNotificationsPage,
  AdminOrderDetailsPage,
  AdminOrdersPage,
  AdminSettingsPage,
  AddEditFoodPage,
  CustomersPage,
  DeliveryPersonnelPage,
  ManageCategoriesPage,
  ManageFoodsPage,
  ReportsPage,
  RevenueAnalyticsPage,
} from "@/pages/admin-pages";
import { ForgotPasswordPage, LandingPage, LoginPage, RegisterPage } from "@/pages/auth-pages";
import {
  AddressFormPage,
  CartPage,
  CategoriesPage,
  CheckoutPage,
  CustomerHomePage,
  FoodDetailsPage,
  OrderDetailsPage,
  OrderHistoryPage,
  OrderSuccessPage,
  PaymentPage,
  ProfilePage,
  SavedAddressesPage,
  SearchResultsPage,
  SettingsPage,
} from "@/pages/customer-pages";
import {
  AssignedOrdersPage,
  DeliveryDashboardPage,
  DeliveryDetailsPage,
  DeliveryHistoryPage,
  DeliveryProfilePage,
} from "@/pages/delivery-pages";

function ProtectedRoute({ roles }: { roles: Array<"CUSTOMER" | "ADMIN" | "DELIVERY_PERSONNEL"> }) {
  const { isAuthenticated, role } = useAuth();
  const location = useLocation();

  if (!isAuthenticated || !role) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  if (!roles.includes(role)) {
    const fallback = role === "ADMIN" ? "/admin/dashboard" : role === "DELIVERY_PERSONNEL" ? "/delivery/dashboard" : "/app/home";
    return <Navigate to={fallback} replace />;
  }

  return <Outlet />;
}

function NotFoundPage() {
  return (
    <div className="flex min-h-screen items-center justify-center p-6">
      <div className="max-w-md text-center">
        <p className="text-sm font-semibold uppercase tracking-[0.3em] text-primary/70">404</p>
        <h1 className="mt-3 text-4xl font-bold">Page not found</h1>
        <p className="mt-3 text-muted-foreground">The route you requested does not exist in this frontend experience.</p>
      </div>
    </div>
  );
}

export const router = createBrowserRouter([
  { path: "/", element: <LandingPage /> },
  { path: "/menu", element: <PublicMenuShell><CategoriesPage /></PublicMenuShell> },
  { path: "/menu/:foodId", element: <PublicMenuShell><FoodDetailsPage /></PublicMenuShell> },
  { path: "/login", element: <LoginPage /> },
  { path: "/delivery/login", element: <LoginPage /> },
  { path: "/register", element: <RegisterPage /> },
  { path: "/forgot-password", element: <ForgotPasswordPage /> },
  {
    element: <ProtectedRoute roles={["CUSTOMER"]} />,
    children: [
      {
        path: "/app",
        element: <CustomerShell />,
        children: [
          { index: true, element: <Navigate to="/app/home" replace /> },
          { path: "home", element: <CustomerHomePage /> },
          { path: "categories", element: <CategoriesPage /> },
          { path: "foods/:foodId", element: <FoodDetailsPage /> },
          { path: "search", element: <SearchResultsPage /> },
          { path: "cart", element: <CartPage /> },
          { path: "checkout", element: <CheckoutPage /> },
          { path: "payment", element: <PaymentPage /> },
          { path: "order-success", element: <OrderSuccessPage /> },
          { path: "orders", element: <OrderHistoryPage /> },
          { path: "orders/:orderId", element: <OrderDetailsPage /> },
          { path: "addresses", element: <SavedAddressesPage /> },
          { path: "addresses/new", element: <AddressFormPage /> },
          { path: "addresses/:addressId/edit", element: <AddressFormPage /> },
          { path: "profile", element: <ProfilePage /> },
          { path: "settings", element: <SettingsPage /> },
        ],
      },
    ],
  },
  {
    element: <ProtectedRoute roles={["ADMIN"]} />,
    children: [
      {
        path: "/admin",
        element: <AdminShell />,
        children: [
          { index: true, element: <Navigate to="/admin/dashboard" replace /> },
          { path: "dashboard", element: <AdminDashboardPage /> },
          { path: "categories", element: <ManageCategoriesPage /> },
          { path: "foods", element: <ManageFoodsPage /> },
          { path: "foods/new", element: <AddEditFoodPage /> },
          { path: "foods/:foodId/edit", element: <AddEditFoodPage /> },
          { path: "orders", element: <AdminOrdersPage /> },
          { path: "orders/:orderId", element: <AdminOrderDetailsPage /> },
          { path: "customers", element: <CustomersPage /> },
          { path: "delivery", element: <DeliveryPersonnelPage /> },
          { path: "reports", element: <ReportsPage /> },
          { path: "revenue", element: <RevenueAnalyticsPage /> },
          { path: "notifications", element: <AdminNotificationsPage /> },
          { path: "settings", element: <AdminSettingsPage /> },
        ],
      },
    ],
  },
  {
    element: <ProtectedRoute roles={["DELIVERY_PERSONNEL"]} />,
    children: [
      {
        path: "/delivery",
        element: <DeliveryShell />,
        children: [
          { index: true, element: <Navigate to="/delivery/dashboard" replace /> },
          { path: "dashboard", element: <DeliveryDashboardPage /> },
          { path: "orders", element: <AssignedOrdersPage /> },
          { path: "orders/:deliveryId", element: <DeliveryDetailsPage /> },
          { path: "history", element: <DeliveryHistoryPage /> },
          { path: "profile", element: <DeliveryProfilePage /> },
        ],
      },
    ],
  },
  { path: "*", element: <NotFoundPage /> },
]);
