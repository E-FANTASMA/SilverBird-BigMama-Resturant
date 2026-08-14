import {
  ChevronLeft,
  Bell,
  Bike,
  CreditCard,
  Home,
  LayoutDashboard,
  LogOut,
  MapPinned,
  MenuSquare,
  Package,
  Search,
  Settings,
  ShoppingBag,
  Soup,
  UserRound,
  Users,
} from "lucide-react";
import { Link, NavLink, Outlet, useLocation, useNavigate } from "react-router-dom";
import type { ReactNode } from "react";
import { useAuth } from "@/auth/auth-store";
import { useLogout } from "@/api/hooks";
import { Button, Card, SearchInput, cn } from "@/components/ui";

type NavItem = {
  to: string;
  label: string;
  icon: ReactNode;
};

const customerNav: NavItem[] = [
  { to: "/app/home", label: "Home", icon: <Home className="h-4 w-4" /> },
  { to: "/app/categories", label: "Menu", icon: <MenuSquare className="h-4 w-4" /> },
  { to: "/app/cart", label: "Cart", icon: <ShoppingBag className="h-4 w-4" /> },
  { to: "/app/orders", label: "Orders", icon: <Package className="h-4 w-4" /> },
  { to: "/app/addresses", label: "Addresses", icon: <MapPinned className="h-4 w-4" /> },
  { to: "/app/profile", label: "Profile", icon: <UserRound className="h-4 w-4" /> },
];

const adminNav: NavItem[] = [
  { to: "/admin/dashboard", label: "Dashboard", icon: <LayoutDashboard className="h-4 w-4" /> },
  { to: "/admin/categories", label: "Categories", icon: <MenuSquare className="h-4 w-4" /> },
  { to: "/admin/foods", label: "Foods", icon: <ShoppingBag className="h-4 w-4" /> },
  { to: "/admin/orders", label: "Orders", icon: <Package className="h-4 w-4" /> },
  { to: "/admin/customers", label: "Customers", icon: <Users className="h-4 w-4" /> },
  { to: "/admin/delivery", label: "Delivery", icon: <Bike className="h-4 w-4" /> },
  { to: "/admin/reports", label: "Reports", icon: <CreditCard className="h-4 w-4" /> },
  { to: "/admin/settings", label: "Settings", icon: <Settings className="h-4 w-4" /> },
];

const deliveryNav: NavItem[] = [
  { to: "/delivery/dashboard", label: "Dashboard", icon: <LayoutDashboard className="h-4 w-4" /> },
  { to: "/delivery/orders", label: "Assigned", icon: <Package className="h-4 w-4" /> },
  { to: "/delivery/history", label: "History", icon: <Bike className="h-4 w-4" /> },
  { to: "/delivery/profile", label: "Profile", icon: <UserRound className="h-4 w-4" /> },
];

export function MarketingShell({ children }: { children: ReactNode }) {
  return (
    <div className="relative overflow-hidden">
      <div className="pointer-events-none absolute inset-0 bg-velvet" />
      <div className="relative mx-auto min-h-screen max-w-7xl px-4 py-6 sm:px-6 lg:px-8">{children}</div>
    </div>
  );
}

export function DashboardShell({ nav, title }: { nav: NavItem[]; title: string }) {
  const navigate = useNavigate();
  const { setSession } = useAuth();
  const logout = useLogout();

  const handleLogout = async () => {
    await logout.mutateAsync();
    setSession(null);
    navigate("/login");
  };

  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top_left,rgba(194,154,76,0.12),transparent_24%),linear-gradient(180deg,rgba(255,251,247,1),rgba(247,243,240,1))]">
      <div className="mx-auto grid max-w-7xl gap-6 px-4 py-6 lg:grid-cols-[280px_minmax(0,1fr)] lg:px-6">
        <Card className="h-fit p-4 lg:sticky lg:top-6">
          <div className="space-y-6">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.3em] text-primary/70">Silverbird</p>
              <h1 className="mt-2 text-2xl font-bold">{title}</h1>
            </div>
            <nav className="space-y-2">
              {nav.map((item) => (
                <NavLink
                  key={item.to}
                  to={item.to}
                  className={({ isActive }) =>
                    cn(
                      "flex items-center gap-3 rounded-2xl px-4 py-3 text-sm font-medium transition",
                      isActive ? "bg-primary text-white shadow-soft" : "text-muted-foreground hover:bg-secondary hover:text-foreground",
                    )
                  }
                >
                  {item.icon}
                  {item.label}
                </NavLink>
              ))}
            </nav>
            <Button variant="outline" className="w-full justify-start" onClick={handleLogout}>
              <LogOut className="h-4 w-4" />
              Logout
            </Button>
          </div>
        </Card>
        <div className="space-y-6">
          <Card className="p-4 sm:p-5">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Welcome back</p>
                <h2 className="text-xl font-semibold">Premium restaurant operations, beautifully organized.</h2>
              </div>
              <div className="flex items-center gap-3">
                <div className="hidden w-72 sm:block">
                  <SearchInput />
                </div>
                <Button variant="outline" size="icon">
                  <Bell className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </Card>
          <div className="animate-fade-up">
            <Outlet />
          </div>
        </div>
      </div>
    </div>
  );
}

export function CustomerShell() {
  return <DashboardShell nav={customerNav} title="Customer" />;
}

export function AdminShell() {
  return <DashboardShell nav={adminNav} title="Admin Suite" />;
}

export function DeliveryShell() {
  return <DashboardShell nav={deliveryNav} title="Delivery Hub" />;
}

export function PublicMenuShell({ children }: { children: ReactNode }) {
  const location = useLocation();
  const isDetailPage = /^\/menu\/.+/.test(location.pathname);

  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top_left,rgba(194,154,76,0.14),transparent_22%),linear-gradient(180deg,#fffdf9,#f6f1ec)]">
      <div className="border-b border-border/60 bg-white/85 backdrop-blur-sm">
        <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex items-center gap-3">
            {isDetailPage ? (
              <Link
                to="/menu"
                className="inline-flex h-11 w-11 items-center justify-center rounded-full border border-border bg-white text-muted-foreground transition hover:border-primary/40 hover:text-primary"
              >
                <ChevronLeft className="h-5 w-5" />
              </Link>
            ) : (
              <div className="flex h-11 w-11 items-center justify-center rounded-full bg-primary text-white shadow-soft">
                <Soup className="h-5 w-5" />
              </div>
            )}
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.3em] text-primary/70">Silverbird</p>
              <h1 className="text-lg font-semibold text-foreground sm:text-xl">
                {isDetailPage ? "Meal Details" : "Restaurant Menu"}
              </h1>
            </div>
          </div>

          <div className="hidden items-center gap-3 sm:flex">
            <Link to="/">
              <Button variant="ghost" size="sm">Home</Button>
            </Link>
            <Link to="/login">
              <Button variant="outline" size="sm">Sign In</Button>
            </Link>
          </div>
        </div>
      </div>

      <div className="mx-auto max-w-6xl px-4 py-8 sm:px-6 lg:px-8">
        {children}
      </div>
    </div>
  );
}
