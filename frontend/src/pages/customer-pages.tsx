import { zodResolver } from "@hookform/resolvers/zod";
import {
  ArrowRight,
  CheckCircle2,
  Clock3,
  Heart,
  MapPinned,
  Minus,
  Plus,
  Settings2,
  ShoppingBag,
  Sparkles,
  Star,
  Truck,
} from "lucide-react";
import type { ReactNode } from "react";
import { useEffect, useMemo, useState } from "react";
import { useForm } from "react-hook-form";
import { Link, useLocation, useNavigate, useParams, useSearchParams } from "react-router-dom";
import { z } from "zod";
import {
  useAddToCart,
  useAddresses,
  useCart,
  useCategories,
  useCreateAddress,
  useCreateOrder,
  useFood,
  useFoods,
  useInitializePayment,
  useOrder,
  useOrders,
  useProfile,
  useUpdateAddress,
  useUpdateCartItem,
  useVerifyPayment,
} from "@/api/hooks";
import { useAuth } from "@/auth/auth-store";
import { demoOrders, heroStats, promoCards } from "@/lib/mock";
import { formatCurrency, formatDate } from "@/lib/format";
import { resolveFoodImage } from "@/lib/food-images";
import {
  AppDialog,
  Badge,
  Button,
  Card,
  EmptyState,
  ErrorState,
  FilterChip,
  FoodCard,
  LoadingState,
  Pagination,
  SearchInput,
  SectionHeading,
  Select,
  Skeleton,
  StatCard,
  TextArea,
  TextInput,
} from "@/components/ui";

const addressSchema = z.object({
  label: z.string().min(1),
  address: z.string().min(5),
  city: z.string().min(1),
  state: z.string().min(1),
  phone: z.string().min(8),
  latitude: z.string().refine((value) => !value || Number.isFinite(Number(value)), "Latitude must be a number").optional(),
  longitude: z.string().refine((value) => !value || Number.isFinite(Number(value)), "Longitude must be a number").optional(),
});
type AddressFormValues = z.infer<typeof addressSchema>;

const profileSchema = z.object({
  first_name: z.string().min(1),
  last_name: z.string().min(1),
  phone: z.string().min(8),
});

export function CustomerHomePage() {
  const { data: foods, isLoading: foodsLoading, isError: foodsError } = useFoods();
  const { data: categories, isLoading: categoriesLoading, isError: categoriesError } = useCategories();

  return (
    <div className="space-y-8">
      <Card className="overflow-hidden bg-[linear-gradient(135deg,rgba(99,18,34,1),rgba(150,40,58,0.88))] p-6 text-white sm:p-8">
        <div className="grid gap-6 lg:grid-cols-[1fr_320px]">
          <div className="space-y-5">
            <Badge>Freshly prepared today</Badge>
            <div className="space-y-3">
              <h1 className="max-w-2xl text-3xl font-bold sm:text-5xl">Order chef-crafted favourites with a premium, delivery-first experience.</h1>
              <p className="max-w-xl text-sm text-white/80 sm:text-base">
                Browse the menu, add items to your cart, and checkout when you are ready.
              </p>
            </div>
            <div className="flex flex-col gap-3 sm:flex-row">
              <Link to="/app/categories">
                <Button variant="secondary" size="lg">
                  Browse menu
                </Button>
              </Link>
              <Link to="/app/cart">
                <Button variant="outline" size="lg" className="border-white/25 bg-white/10 text-white hover:bg-white/15">
                  Open cart
                </Button>
              </Link>
            </div>
          </div>
          <Card className="grid gap-4 bg-white/10 p-5 text-white backdrop-blur">
            {heroStats.map((stat) => (
              <div key={stat.label} className="rounded-2xl border border-white/10 bg-white/10 p-4">
                <p className="text-sm text-white/70">{stat.label}</p>
                <p className="mt-2 text-2xl font-bold">{stat.value}</p>
              </div>
            ))}
          </Card>
        </div>
      </Card>

      <div className="grid gap-4 lg:grid-cols-2">
        {promoCards.map((promo) => (
          <Card key={promo.title} className="p-6">
            <p className="text-xs font-semibold uppercase tracking-[0.25em] text-primary/70">Restaurant highlight</p>
            <h3 className="mt-3 text-xl font-semibold">{promo.title}</h3>
            <p className="mt-2 text-sm text-muted-foreground">{promo.copy}</p>
          </Card>
        ))}
      </div>

      <section className="space-y-4">
        <SectionHeading eyebrow="Collections" title="Browse by category" />
        {categoriesLoading ? (
          <LoadingState label="Loading menu categories..." />
        ) : categoriesError ? (
          <ErrorState title="Could not load categories" description="Menu categories are unavailable right now. Please try again." />
        ) : (
          <div className="flex flex-wrap gap-3">
            {categories?.map((category) => (
              <FilterChip key={category.id} label={category.name} />
            ))}
          </div>
        )}
      </section>

      <section className="space-y-4">
        <SectionHeading title="Popular right now" />
        {foodsLoading ? (
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            {Array.from({ length: 4 }).map((_, index) => (
              <Skeleton key={index} className="h-80" />
            ))}
          </div>
        ) : foodsError ? (
          <ErrorState title="Could not load menu items" description="Popular dishes could not be loaded. Please try again." />
        ) : (
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            {foods?.slice(0, 4).map((food) => (
              <FoodCard
                key={food.id}
                image={resolveFoodImage(food)}
                title={food.name}
                description={food.description}
                price={formatCurrency(food.price)}
                meta={`${food.preparation_time_minutes ?? 15} mins`}
                action={
                  <Link to={`/app/foods/${food.id}`}>
                    <Button size="sm">View</Button>
                  </Link>
                }
              />
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

export function CategoriesPage() {
  const location = useLocation();
  const { data: categories, isLoading: categoriesLoading, isError: categoriesError } = useCategories();
  const { data: foods, isLoading: foodsLoading, isError: foodsError } = useFoods();
  const [activeCategory, setActiveCategory] = useState<string>("all");
  const detailBasePath = location.pathname.startsWith("/menu") ? "/menu" : "/app/foods";
  const isPublicMenu = location.pathname.startsWith("/menu");

  const visibleFoods = useMemo(
    () => foods?.filter((food) => activeCategory === "all" || food.category_id === activeCategory) ?? [],
    [foods, activeCategory],
  );

  return (
    <div className="space-y-8">
      {isPublicMenu ? (
        <Card className="overflow-hidden rounded-[2rem] border-white/70 bg-[linear-gradient(135deg,rgba(99,18,34,0.96),rgba(143,43,59,0.88))] p-6 text-white shadow-float sm:p-8">
          <div className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr] lg:items-end">
            <div className="space-y-4">
              <p className="text-xs font-semibold uppercase tracking-[0.35em] text-white/75">Freshly prepared</p>
              <h2 className="max-w-2xl text-3xl font-bold tracking-tight sm:text-5xl">
                Explore the full BigMama menu without the clutter.
              </h2>
              <p className="max-w-xl text-sm leading-7 text-white/82 sm:text-base">
                Browse signature rice plates, shawarma, soups, noodles, and quick bites in a tighter, easier-to-scan layout.
              </p>
            </div>
            <div className="rounded-[1.5rem] border border-white/14 bg-white/10 p-5 backdrop-blur-sm">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-xs uppercase tracking-[0.25em] text-white/65">Categories</p>
                  <p className="mt-2 text-2xl font-bold">{categories?.length ?? 0}</p>
                </div>
                <div>
                  <p className="text-xs uppercase tracking-[0.25em] text-white/65">Meals</p>
                  <p className="mt-2 text-2xl font-bold">{visibleFoods.length}</p>
                </div>
              </div>
            </div>
          </div>
        </Card>
      ) : (
        <SectionHeading title="Menu Categories" />
      )}

      {categoriesLoading ? (
        <LoadingState label="Loading menu categories..." />
      ) : categoriesError ? (
        <ErrorState title="Could not load categories" description="Menu categories could not be loaded. Please try again." />
      ) : (
        <Card className="rounded-[2rem] border-white/70 p-4 sm:p-5">
          <div className="flex flex-wrap gap-3">
            <FilterChip label="All" active={activeCategory === "all"} onClick={() => setActiveCategory("all")} />
            {categories?.map((category) => (
              <FilterChip
                key={category.id}
                label={category.name}
                active={activeCategory === category.id}
                onClick={() => setActiveCategory(category.id)}
              />
            ))}
          </div>
        </Card>
      )}

      {foodsLoading ? (
        <LoadingState label="Loading menu categories..." />
      ) : foodsError ? (
        <ErrorState title="Could not load menu items" description="Menu items could not be loaded. Please try again." />
      ) : visibleFoods.length === 0 ? (
        <EmptyState title="No meals here yet" description="There are no meals in this category yet." />
      ) : (
        <div className="grid gap-5 lg:grid-cols-2 xl:grid-cols-3">
          {visibleFoods.map((food) => (
            <FoodCard
              key={food.id}
              image={resolveFoodImage(food)}
              title={food.name}
              description={food.description}
              price={formatCurrency(food.price)}
              meta={`${food.preparation_time_minutes ?? 15} mins`}
              action={
                <Link to={`${detailBasePath}/${food.id}`}>
                  <Button size="sm">Open</Button>
                </Link>
              }
            />
          ))}
        </div>
      )}
    </div>
  );
}

export function FoodDetailsPage() {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const { foodId = "" } = useParams();
  const { data: food, isLoading, isError } = useFood(foodId);
  const addToCart = useAddToCart();
  const [quantity, setQuantity] = useState(1);
  const isPublicMenu = location.pathname.startsWith("/menu");

  if (isLoading) {
    return <LoadingState label="Loading meal details..." />;
  }

  if (isError) {
    return <ErrorState title="Could not load meal" description="This meal could not be loaded. Please try again." />;
  }

  if (!food) {
    return <ErrorState title="Food not found" description="We couldn't find that meal." />;
  }

  return (
    <div className="grid gap-6 xl:grid-cols-[1.05fr_0.95fr]">
      <Card className="overflow-hidden rounded-[2rem]">
        <img className="h-full w-full object-cover" src={resolveFoodImage(food)} alt={food.name} />
      </Card>
      <Card className="rounded-[2rem] p-6 sm:p-8">
        <div className="space-y-5">
          <div className="flex flex-wrap items-center gap-3">
            <Badge>Signature plate</Badge>
            <Badge tone="warning">
              <Star className="mr-1 h-3 w-3" />
              4.8 rating
            </Badge>
          </div>
          <div>
            <h1 className="text-3xl font-bold">{food.name}</h1>
            <p className="mt-3 text-muted-foreground">{food.description}</p>
          </div>
          <div className="grid gap-3 sm:grid-cols-3">
            <StatCard label="Price" value={formatCurrency(food.price)} />
            <StatCard label="Prep time" value={`${food.preparation_time_minutes ?? 15} mins`} />
            <StatCard label="Availability" value={food.is_available ? "Available" : "Unavailable"} />
          </div>
          <div className="rounded-3xl border border-border bg-secondary/40 p-4">
            <div className="flex items-center justify-between">
              <p className="text-sm font-medium">Quantity</p>
              <div className="flex items-center gap-3">
                <Button variant="outline" size="icon" onClick={() => setQuantity((value) => Math.max(1, value - 1))}>
                  <Minus className="h-4 w-4" />
                </Button>
                <span className="min-w-8 text-center font-semibold">{quantity}</span>
                <Button variant="outline" size="icon" onClick={() => setQuantity((value) => value + 1)}>
                  <Plus className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </div>
          <div className="flex flex-col gap-3 sm:flex-row">
            <Button
              size="lg"
              className="flex-1"
              onClick={() => {
                if (!isAuthenticated && isPublicMenu) {
                  navigate("/login", { state: { from: { pathname: `/menu/${food.id}` } } });
                  return;
                }
                addToCart.mutate({ food_item_id: food.id, quantity });
              }}
            >
              {isAuthenticated ? "Add to cart" : "Sign in to order"}
            </Button>
            <Button variant="outline" size="lg">
              <Heart className="h-4 w-4" />
              Save
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
}

export function SearchResultsPage() {
  const location = useLocation();
  const [params, setParams] = useSearchParams();
  const query = params.get("q") ?? "";
  const { data: foods, isLoading, isError } = useFoods();
  const [page, setPage] = useState(1);
  const filtered = foods?.filter((food) => food.name.toLowerCase().includes(query.toLowerCase())) ?? [];
  const pageFoods = filtered.slice((page - 1) * 6, page * 6);
  const detailBasePath = location.pathname.startsWith("/menu") ? "/menu" : "/app/foods";

  return (
    <div className="space-y-6">
      <SectionHeading title="Search Results" description={query ? `Results for "${query}".` : undefined} />
      <div className="grid gap-4 sm:grid-cols-[1fr_auto]">
        <SearchInput value={query} onChange={(event) => setParams({ q: event.target.value })} />
        <Button variant="outline">
          <Settings2 className="h-4 w-4" />
          Sort & Filter
        </Button>
      </div>
      {isLoading ? (
        <LoadingState label="Loading search results..." />
      ) : isError ? (
        <ErrorState title="Could not search menu" description="Search is unavailable right now. Please try again." />
      ) : pageFoods.length === 0 ? (
        <EmptyState title="No results yet" description="Try another search term or explore full categories." />
      ) : (
        <>
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {pageFoods.map((food) => (
              <FoodCard
                key={food.id}
                image={resolveFoodImage(food)}
                title={food.name}
                description={food.description}
                price={formatCurrency(food.price)}
                meta="Popular pick"
                action={
                  <Link to={`${detailBasePath}/${food.id}`}>
                    <Button size="sm">Details</Button>
                  </Link>
                }
              />
            ))}
          </div>
          <Pagination page={page} pageCount={Math.max(1, Math.ceil(filtered.length / 6))} onChange={setPage} />
        </>
      )}
    </div>
  );
}

export function CartPage() {
  const { data: cart, isLoading } = useCart();
  const updateItem = useUpdateCartItem();
  const navigate = useNavigate();

  if (isLoading) {
    return <LoadingState label="Loading your cart..." />;
  }

  if (!cart || cart.items.length === 0) {
    return <EmptyState title="Your cart is empty" description="Add a few standout dishes to continue." action={<Link to="/app/categories"><Button>Browse menu</Button></Link>} />;
  }

  return (
    <div className="grid gap-6 xl:grid-cols-[1.15fr_0.85fr]">
      <div className="space-y-4">
        <SectionHeading title="Your Cart" />
        {cart.items.map((item) => (
          <Card key={item.id} className="p-5">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <h3 className="font-semibold">{item.food_name}</h3>
                <p className="mt-1 text-sm text-muted-foreground">{formatCurrency(item.unit_price)} each</p>
              </div>
              <div className="flex items-center gap-3">
                <Button variant="outline" size="icon" onClick={() => updateItem.mutate({ itemId: item.id, quantity: Math.max(1, item.quantity - 1) })}>
                  <Minus className="h-4 w-4" />
                </Button>
                <span className="min-w-6 text-center font-semibold">{item.quantity}</span>
                <Button variant="outline" size="icon" onClick={() => updateItem.mutate({ itemId: item.id, quantity: item.quantity + 1 })}>
                  <Plus className="h-4 w-4" />
                </Button>
                <Badge>{formatCurrency(item.subtotal)}</Badge>
              </div>
            </div>
          </Card>
        ))}
      </div>
      <Card className="h-fit p-6">
        <SectionHeading title="Summary" />
        <div className="mt-6 space-y-4 text-sm">
          <SummaryRow label="Subtotal" value={formatCurrency(cart.subtotal)} />
          <SummaryRow label="Delivery fee" value={formatCurrency(cart.delivery_fee)} />
          <SummaryRow label="Tax" value={formatCurrency(cart.tax_amount)} />
          <SummaryRow label="Discount" value={formatCurrency(cart.discount_amount)} />
          <div className="border-t border-border pt-4">
            <SummaryRow label="Grand total" value={formatCurrency(cart.grand_total)} strong />
          </div>
        </div>
        <Button className="mt-6 w-full" size="lg" onClick={() => navigate("/app/checkout")}>
          Proceed to checkout
        </Button>
        <Button className="mt-3 w-full" variant="outline" onClick={() => navigate("/app/addresses")}>
          Manage delivery addresses
        </Button>
      </Card>
    </div>
  );
}

export function CheckoutPage() {
  const { data: addresses } = useAddresses();
  const { data: cart } = useCart();
  const createOrder = useCreateOrder();
  const navigate = useNavigate();
  const [orderType, setOrderType] = useState<"DELIVERY" | "PICKUP" | "DINE_IN">("DELIVERY");
  const [addressId, setAddressId] = useState("");
  const [tableNumber, setTableNumber] = useState("");
  const [scheduledPickupTime, setScheduledPickupTime] = useState("");
  const [notes, setNotes] = useState("");

  useEffect(() => {
    if (!addresses || addresses.length === 0) {
      if (addressId) {
        setAddressId("");
      }
      return;
    }

    const selectedAddressStillExists = addresses.some((address) => address.id === addressId);
    if (selectedAddressStillExists) {
      return;
    }

    const preferredAddress = addresses.find((address) => address.is_default) ?? addresses[0];
    setAddressId(preferredAddress.id);
  }, [addresses, addressId]);

  if (!cart || cart.items.length === 0) {
    return (
      <EmptyState
        title="Your cart is empty"
        description="Add a few meals before heading into checkout."
        action={
          <Link to="/app/categories">
            <Button>Browse menu</Button>
          </Link>
        }
      />
    );
  }

  const submitOrder = async () => {
    const order = await createOrder.mutateAsync({
      order_type: orderType,
      delivery_address_id: orderType === "DELIVERY" ? addressId : null,
      scheduled_pickup_time: orderType === "PICKUP" ? new Date(scheduledPickupTime).toISOString() : null,
      table_number: orderType === "DINE_IN" ? tableNumber : null,
      notes,
    });
    navigate(`/app/payment?orderId=${order.id}`);
  };

  return (
    <div className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
      <div className="space-y-6">
        <SectionHeading title="Checkout" description="Choose how you want to receive your order and confirm your details." />
        <Card className="p-6">
          <h3 className="font-semibold">Order type</h3>
          <div className="mt-4 flex flex-wrap gap-3">
            {(["DELIVERY", "PICKUP", "DINE_IN"] as const).map((item) => (
              <FilterChip key={item} label={item.replace("_", " ")} active={orderType === item} onClick={() => setOrderType(item)} />
            ))}
          </div>
        </Card>
        {orderType === "DELIVERY" ? (
          <Card className="p-6">
            <h3 className="font-semibold">Delivery address</h3>
            {addresses && addresses.length > 0 ? (
              <div className="mt-4 grid gap-3">
                {addresses.map((address) => (
                  <button
                    key={address.id}
                    type="button"
                    onClick={() => setAddressId(address.id)}
                    className={`rounded-2xl border p-4 text-left transition ${addressId === address.id ? "border-primary bg-primary/5" : "border-border bg-white"}`}
                  >
                    <div className="flex items-center justify-between">
                      <p className="font-medium">{address.label}</p>
                      {address.is_default ? <Badge tone="success">Default</Badge> : null}
                    </div>
                    <p className="mt-2 text-sm text-muted-foreground">{address.address}, {address.city}, {address.state}</p>
                  </button>
                ))}
              </div>
            ) : (
              <EmptyState
                title="No saved addresses yet"
                description="Add a delivery address first so you can complete checkout."
                action={
                  <Link to="/app/addresses/new">
                    <Button>Add address</Button>
                  </Link>
                }
              />
            )}
          </Card>
        ) : null}
        {orderType === "PICKUP" ? (
          <Card className="p-6">
            <Field label="Pickup time">
              <TextInput
                type="datetime-local"
                value={scheduledPickupTime}
                onChange={(event) => setScheduledPickupTime(event.target.value)}
              />
            </Field>
          </Card>
        ) : null}
        {orderType === "DINE_IN" ? (
          <Card className="p-6">
            <Field label="Table number">
              <TextInput value={tableNumber} onChange={(event) => setTableNumber(event.target.value)} placeholder="e.g. A12" />
            </Field>
          </Card>
        ) : null}
        <Card className="p-6">
          <Field label="Order notes">
            <TextArea value={notes} onChange={(event) => setNotes(event.target.value)} placeholder="Special requests, drop-off notes, spice preference..." />
          </Field>
        </Card>
      </div>
      <Card className="h-fit p-6">
        <SectionHeading title="Order recap" />
        <div className="mt-6 space-y-4">
          <SummaryRow label="Items" value={`${cart.total_items}`} />
          <SummaryRow label="Estimated total" value={formatCurrency(cart.grand_total)} strong />
        </div>
        <Button
          className="mt-6 w-full"
          size="lg"
          onClick={submitOrder}
          disabled={
            createOrder.isPending ||
            (orderType === "DELIVERY" && !addressId) ||
            (orderType === "PICKUP" && !scheduledPickupTime) ||
            (orderType === "DINE_IN" && !tableNumber.trim())
          }
        >
          {createOrder.isPending ? "Creating order..." : "Continue to payment"}
        </Button>
      </Card>
    </div>
  );
}

export function PaymentPage() {
  const [params] = useSearchParams();
  const orderId = params.get("orderId") ?? demoOrders[0].id;
  const initializePayment = useInitializePayment();
  const navigate = useNavigate();

  const handlePayment = async () => {
    const response = await initializePayment.mutateAsync(orderId);
    window.open(response.authorization_url, "_blank", "noopener,noreferrer");
    navigate(`/app/order-success?reference=${response.reference}`);
  };

  return (
    <div className="grid gap-6 xl:grid-cols-[1fr_0.9fr]">
      <Card className="p-6 sm:p-8">
        <SectionHeading title="Payment" description="Choose how you would like to pay." />
        <div className="mt-6 grid gap-4 sm:grid-cols-2">
          {["Card", "Bank Transfer", "Wallet"].map((option) => (
            <Card key={option} className="p-5">
              <h3 className="font-semibold">{option}</h3>
            </Card>
          ))}
        </div>
      </Card>
      <Card className="h-fit p-6">
        <SectionHeading title="Ready to pay?" description="Click below to open the secure payment window and complete your order." />
        <Button className="mt-6 w-full" size="lg" onClick={handlePayment} disabled={initializePayment.isPending}>
          {initializePayment.isPending ? "Opening payment..." : "Pay now"}
        </Button>
      </Card>
    </div>
  );
}

export function OrderSuccessPage() {
  const [params] = useSearchParams();
  const reference = params.get("reference") ?? "demo-reference";
  const { data } = useVerifyPayment(reference);

  return (
    <Card className="mx-auto max-w-2xl p-8 text-center">
      <div className="mx-auto flex h-20 w-20 items-center justify-center rounded-full bg-success/10 text-success">
        <CheckCircle2 className="h-10 w-10" />
      </div>
      <h1 className="mt-6 text-3xl font-bold">Order placed successfully</h1>
      <p className="mt-3 text-muted-foreground">
        Payment reference <span className="font-semibold text-foreground">{reference}</span> has status {data?.status ?? "SUCCESSFUL"}.
      </p>
      <div className="mt-8 flex flex-col justify-center gap-3 sm:flex-row">
        <Link to="/app/orders">
          <Button>View order history</Button>
        </Link>
        <Link to="/app/home">
          <Button variant="outline">Continue shopping</Button>
        </Link>
      </div>
    </Card>
  );
}

export function OrderHistoryPage() {
  const { data: orders } = useOrders();
  return (
    <div className="space-y-6">
      <SectionHeading title="Order History" />
      <div className="grid gap-4">
        {orders?.map((order) => (
          <Card key={order.id} className="p-5">
            <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
              <div>
                <div className="flex items-center gap-3">
                  <h3 className="font-semibold">{order.order_number}</h3>
                  <StatusBadge status={order.status} />
                </div>
                <p className="mt-2 text-sm text-muted-foreground">{formatDate(order.created_at)} • {order.items.length} items</p>
              </div>
              <div className="flex items-center gap-3">
                <Badge>{formatCurrency(order.total)}</Badge>
                <Link to={`/app/orders/${order.id}`}>
                  <Button variant="outline" size="sm">Details</Button>
                </Link>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}

export function OrderDetailsPage() {
  const { orderId = "" } = useParams();
  const { data: order } = useOrder(orderId);

  if (!order) {
    return <ErrorState title="Order unavailable" description="We couldn't load that order." />;
  }

  return (
    <div className="grid gap-6 xl:grid-cols-[1fr_0.9fr]">
      <Card className="p-6">
        <SectionHeading title={`Order ${order.order_number}`} />
        <div className="mt-6 space-y-4">
          {order.items.map((item) => (
            <div key={item.id} className="flex items-center justify-between rounded-2xl border border-border p-4">
              <div>
                <p className="font-medium">{item.food_name_snapshot}</p>
                <p className="text-sm text-muted-foreground">Qty {item.quantity}</p>
              </div>
              <Badge>{formatCurrency(item.subtotal)}</Badge>
            </div>
          ))}
        </div>
      </Card>
      <Card className="p-6">
        <SectionHeading title="Summary" />
        <div className="mt-6 space-y-4">
          <SummaryRow label="Status" value={order.status.replace(/_/g, " ")} />
          <SummaryRow label="Payment" value={order.payment_status} />
          <SummaryRow label="Order type" value={order.order_type.replace(/_/g, " ")} />
          <SummaryRow label="Total" value={formatCurrency(order.total)} strong />
        </div>
      </Card>
    </div>
  );
}

export function SavedAddressesPage() {
  const { data: addresses } = useAddresses();

  return (
    <div className="space-y-6">
      <SectionHeading
        title="Saved Addresses"
        action={<Link to="/app/addresses/new"><Button>Add address</Button></Link>}
      />
      {addresses && addresses.length > 0 ? (
        <div className="grid gap-4 md:grid-cols-2">
          {addresses.map((address) => (
            <Card key={address.id} className="p-5">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <div className="flex items-center gap-2">
                    <MapPinned className="h-4 w-4 text-primary" />
                    <h3 className="font-semibold">{address.label}</h3>
                  </div>
                  <p className="mt-3 text-sm text-muted-foreground">{address.address}, {address.city}, {address.state}</p>
                </div>
                {address.is_default ? <Badge tone="success">Default</Badge> : null}
              </div>
              <div className="mt-5 flex gap-3">
                <Link to={`/app/addresses/${address.id}/edit`}>
                  <Button variant="outline" size="sm">Edit</Button>
                </Link>
              </div>
            </Card>
          ))}
        </div>
      ) : (
        <EmptyState
          title="No saved addresses yet"
          description="Your saved delivery addresses will appear here once you add one."
          action={
            <Link to="/app/addresses/new">
              <Button>Add your first address</Button>
            </Link>
          }
        />
      )}
    </div>
  );
}

export function AddressFormPage() {
  const navigate = useNavigate();
  const { addressId } = useParams();
  const isEditing = Boolean(addressId);
  const { data: addresses } = useAddresses();
  const createAddress = useCreateAddress();
  const updateAddress = useUpdateAddress();
  const currentAddress = addresses?.find((entry) => entry.id === addressId);
  const initialValues: AddressFormValues = currentAddress
    ? {
        label: currentAddress.label,
        address: currentAddress.address,
        city: currentAddress.city,
        state: currentAddress.state,
        phone: currentAddress.phone,
        latitude: currentAddress.latitude != null ? String(currentAddress.latitude) : "",
        longitude: currentAddress.longitude != null ? String(currentAddress.longitude) : "",
      }
    : { label: "", address: "", city: "", state: "Lagos", phone: "", latitude: "", longitude: "" };

  const onSubmit = async (values: AddressFormValues) => {
    const latitude = values.latitude?.trim() ? Number(values.latitude) : null;
    const longitude = values.longitude?.trim() ? Number(values.longitude) : null;
    const payload = {
      label: values.label,
      address: values.address,
      city: values.city,
      state: values.state,
      phone: values.phone,
      latitude,
      longitude,
    };

    if (isEditing && addressId) {
      await updateAddress.mutateAsync({ addressId, data: payload });
    } else {
      await createAddress.mutateAsync(payload);
    }

    navigate("/app/addresses");
  };

  return (
    <Card className="mx-auto max-w-3xl p-6">
      <SectionHeading title={isEditing ? "Edit Address" : "Add Address"} />
      <AddressEditorForm
        key={currentAddress ? `${currentAddress.id}-${currentAddress.updated_at}` : "new-address"}
        defaultValues={initialValues}
        onSubmit={onSubmit}
        isSaving={createAddress.isPending || updateAddress.isPending}
      />
    </Card>
  );
}

function AddressEditorForm({
  defaultValues,
  onSubmit,
  isSaving,
}: {
  defaultValues: AddressFormValues;
  onSubmit: (values: AddressFormValues) => Promise<void>;
  isSaving: boolean;
}) {
  const form = useForm<AddressFormValues>({
    resolver: zodResolver(addressSchema),
    defaultValues,
  });

  return (
    <form className="mt-6 grid gap-4 sm:grid-cols-2" onSubmit={form.handleSubmit(onSubmit)}>
      <Field label="Label" error={form.formState.errors.label?.message}>
        <TextInput {...form.register("label")} placeholder="Home" />
      </Field>
      <Field label="Phone" error={form.formState.errors.phone?.message}>
        <TextInput {...form.register("phone")} placeholder="+2348012345678" />
      </Field>
      <div className="sm:col-span-2">
        <Field label="Address" error={form.formState.errors.address?.message}>
          <TextInput {...form.register("address")} placeholder="12 Admiralty Way" />
        </Field>
      </div>
      <Field label="City" error={form.formState.errors.city?.message}>
        <TextInput {...form.register("city")} placeholder="Lekki" />
      </Field>
      <Field label="State" error={form.formState.errors.state?.message}>
        <Select {...form.register("state")}>
          <option>Lagos</option>
          <option>FCT</option>
          <option>Rivers</option>
        </Select>
      </Field>
      <Field label="Latitude (optional)" error={form.formState.errors.latitude?.message}>
        <TextInput {...form.register("latitude")} placeholder="6.4698" />
      </Field>
      <Field label="Longitude (optional)" error={form.formState.errors.longitude?.message}>
        <TextInput {...form.register("longitude")} placeholder="3.5852" />
      </Field>
      <div className="sm:col-span-2">
        <Button disabled={isSaving}>{isSaving ? "Saving..." : "Save address"}</Button>
      </div>
    </form>
  );
}

export function ProfilePage() {
  const { data: profile } = useProfile();
  const form = useForm<z.infer<typeof profileSchema>>({
    resolver: zodResolver(profileSchema),
    defaultValues: {
      first_name: profile?.first_name ?? "",
      last_name: profile?.last_name ?? "",
      phone: profile?.phone ?? "",
    },
  });

  return (
    <div className="grid gap-6 xl:grid-cols-[0.8fr_1.2fr]">
      <Card className="p-6 text-center">
        <div className="mx-auto flex h-24 w-24 items-center justify-center rounded-full bg-primary/10 text-3xl font-bold text-primary">
          {profile?.first_name?.[0] ?? "A"}
        </div>
        <h2 className="mt-4 text-2xl font-bold">{profile?.first_name} {profile?.last_name}</h2>
        <p className="mt-2 text-sm text-muted-foreground">{profile?.email}</p>
      </Card>
      <Card className="p-6">
        <SectionHeading title="Profile" description="Update your personal information below." />
        <form className="mt-6 grid gap-4 sm:grid-cols-2">
          <Field label="First name" error={form.formState.errors.first_name?.message}>
            <TextInput {...form.register("first_name")} />
          </Field>
          <Field label="Last name" error={form.formState.errors.last_name?.message}>
            <TextInput {...form.register("last_name")} />
          </Field>
          <div className="sm:col-span-2">
            <Field label="Phone" error={form.formState.errors.phone?.message}>
              <TextInput {...form.register("phone")} />
            </Field>
          </div>
          <div className="sm:col-span-2">
            <Button>Update profile</Button>
          </div>
        </form>
      </Card>
    </div>
  );
}

export function SettingsPage() {
  return (
    <div className="grid gap-4 lg:grid-cols-2">
      {[
        ["Push notifications", "Receive live order and delivery updates."],
        ["Email receipts", "Send order confirmations to your inbox."],
        ["Saved cards", "Control secure payment preferences."],
        ["Privacy controls", "Manage account visibility and personalization."],
      ].map(([title, copy]) => (
        <Card key={title} className="p-6">
          <div className="flex items-start justify-between gap-4">
            <div>
              <h3 className="font-semibold">{title}</h3>
              <p className="mt-2 text-sm text-muted-foreground">{copy}</p>
            </div>
            <div className="h-6 w-11 rounded-full bg-primary p-1">
              <div className="ml-auto h-4 w-4 rounded-full bg-white" />
            </div>
          </div>
        </Card>
      ))}
    </div>
  );
}

function SummaryRow({ label, value, strong = false }: { label: string; value: string; strong?: boolean }) {
  return (
    <div className={`flex items-center justify-between ${strong ? "text-base font-semibold" : "text-sm text-muted-foreground"}`}>
      <span>{label}</span>
      <span className={strong ? "text-foreground" : "text-foreground/85"}>{value}</span>
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const tone = status === "DELIVERED" ? "success" : status === "CANCELLED" ? "danger" : status === "OUT_FOR_DELIVERY" ? "warning" : "default";
  return <Badge tone={tone as "default" | "success" | "warning" | "danger"}>{status.replace(/_/g, " ")}</Badge>;
}

function Field({
  label,
  error,
  children,
}: {
  label: string;
  error?: string;
  children: ReactNode;
}) {
  return (
    <label className="block space-y-2">
      <span className="text-sm font-medium">{label}</span>
      {children}
      {error ? <span className="text-xs text-danger">{error}</span> : null}
    </label>
  );
}
