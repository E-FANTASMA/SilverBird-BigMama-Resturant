import { zodResolver } from "@hookform/resolvers/zod";
import { BarChart3, Bike, DollarSign, Package, Pencil, PlusCircle, Users } from "lucide-react";
import type { ChangeEvent, ReactNode } from "react";
import { useEffect, useMemo, useState } from "react";
import { useForm } from "react-hook-form";
import { Link, useNavigate, useParams } from "react-router-dom";
import { z } from "zod";
import {
  useAdminDashboard,
  useCategories,
  useCreateFood,
  useFood,
  useFoods,
  useOrders,
  useProfile,
  useUpdateFood,
  useUploadFoodImage,
} from "@/api/hooks";
import { formatCurrency, formatDate } from "@/lib/format";
import { demoDeliveryOrders } from "@/lib/mock";
import {
  AppDialog,
  Badge,
  Button,
  Card,
  DataTable,
  EmptyState,
  SectionHeading,
  Select,
  StatCard,
  TextInput,
  TextArea,
} from "@/components/ui";

const foodSchema = z.object({
  name: z.string().min(1),
  category_id: z.string().min(1),
  price: z.string().min(1).refine((value) => Number.isFinite(Number(value)) && Number(value) >= 0, "Price must be a valid amount"),
  description: z.string().min(10),
  preparation_time_minutes: z
    .string()
    .optional()
    .refine((value) => !value || (Number.isInteger(Number(value)) && Number(value) >= 0), "Prep time must be a whole number"),
  is_available: z.enum(["true", "false"]),
});
type FoodFormValues = z.infer<typeof foodSchema>;

export function AdminDashboardPage() {
  const { data } = useAdminDashboard();

  return (
    <div className="space-y-6">
      <SectionHeading title="Dashboard" />
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Total orders" value={`${data?.total_orders ?? 0}`} delta="+12%" />
        <StatCard label="Total customers" value={`${data?.total_customers ?? 0}`} delta="+8%" />
        <StatCard label="Revenue" value={formatCurrency(data?.total_revenue ?? 0)} delta="+18%" />
        <StatCard label="Pending orders" value={`${data?.pending_orders ?? 0}`} />
      </div>
      <div className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
        <RevenueChartCard />
        <Card className="p-6">
          <SectionHeading title="Operational focus" />
          <div className="mt-6 space-y-4">
            {[
              ["Prep line stability", "Kitchen throughput is holding below the 20-minute target."],
              ["Rider assignments", "Three high-value delivery orders need rider allocation."],
              ["Top-selling dishes", "Charcoal chicken and jollof continue to lead conversion."],
            ].map(([title, copy]) => (
              <div key={title} className="rounded-2xl border border-border p-4">
                <p className="font-medium">{title}</p>
                <p className="mt-2 text-sm text-muted-foreground">{copy}</p>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
}

export function ManageCategoriesPage() {
  const { data: categories } = useCategories();
  return (
    <div className="space-y-6">
      <SectionHeading title="Manage Categories" />
      <DataTable
        columns={["Category", "Description", "Sort Order", "Status"]}
        rows={(categories ?? []).map((category) => [
          <span className="font-medium">{category.name}</span>,
          category.description ?? "No description",
          `${category.sort_order}`,
          <Badge tone="success">Active</Badge>,
        ])}
      />
    </div>
  );
}

export function ManageFoodsPage() {
  const { data: foods } = useFoods();
  const { data: categories } = useCategories();
  const updateFood = useUpdateFood();

  return (
    <div className="space-y-6">
      <SectionHeading
        title="Manage Foods"
        action={<Link to="/admin/foods/new"><Button><PlusCircle className="h-4 w-4" /> Add food</Button></Link>}
      />
      <DataTable
        columns={["Food", "Category", "Price", "Availability", "Action"]}
        rows={(foods ?? []).map((food) => [
          <span className="font-medium">{food.name}</span>,
          categories?.find((category) => category.id === food.category_id)?.name ?? "Unassigned",
          formatCurrency(food.price),
          <Button
            variant={food.is_available ? "secondary" : "outline"}
            size="sm"
            disabled={updateFood.isPending}
            onClick={() =>
              updateFood.mutate({
                foodId: food.id,
                data: { is_available: !food.is_available },
              })
            }
          >
            {food.is_available ? "On" : "Off"}
          </Button>,
          <Link to={`/admin/foods/${food.id}/edit`}>
            <Button variant="outline" size="sm">
              <Pencil className="h-4 w-4" />
              Edit
            </Button>
          </Link>,
        ])}
      />
    </div>
  );
}

export function AddEditFoodPage() {
  const navigate = useNavigate();
  const { foodId } = useParams();
  const isEditing = Boolean(foodId);
  const { data: categories } = useCategories();
  const { data: existingFood } = useFood(foodId);
  const createFood = useCreateFood();
  const updateFood = useUpdateFood();
  const uploadFoodImage = useUploadFoodImage();
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [selectedImageName, setSelectedImageName] = useState("");
  const form = useForm<FoodFormValues>({
    resolver: zodResolver(foodSchema),
    defaultValues: {
      name: "",
      category_id: "",
      price: "",
      description: "",
      preparation_time_minutes: "",
      is_available: "true",
    },
  });

  useEffect(() => {
    if (!existingFood) {
      return;
    }

    form.reset({
      name: existingFood.name,
      category_id: existingFood.category_id,
      price: String(existingFood.price),
      description: existingFood.description ?? "",
      preparation_time_minutes: existingFood.preparation_time_minutes != null ? String(existingFood.preparation_time_minutes) : "",
      is_available: existingFood.is_available ? "true" : "false",
    });
  }, [existingFood, form]);

  const isSubmitting = createFood.isPending || updateFood.isPending || uploadFoodImage.isPending;

  const onSelectImage = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0] ?? null;
    setSelectedImage(file);
    setSelectedImageName(file?.name ?? "");
  };

  const onSubmit = async (values: FoodFormValues) => {
    const payload = {
      name: values.name,
      category_id: values.category_id,
      price: Number(values.price),
      description: values.description,
      preparation_time_minutes: values.preparation_time_minutes?.trim() ? Number(values.preparation_time_minutes) : null,
      is_available: values.is_available === "true",
    };

    const savedFood = isEditing && foodId
      ? await updateFood.mutateAsync({ foodId, data: payload })
      : await createFood.mutateAsync(payload);

    if (selectedImage) {
      await uploadFoodImage.mutateAsync({ foodId: savedFood.id, file: selectedImage });
    }

    navigate("/admin/foods");
  };

  return (
    <Card className="mx-auto max-w-4xl p-6">
      <SectionHeading
        title={isEditing ? "Edit Food" : "Add Food"}
        description="Save the meal details, choose whether it is currently available, and optionally attach a food image."
      />
      <form className="mt-6 grid gap-4 sm:grid-cols-2" onSubmit={form.handleSubmit(onSubmit)}>
        <Field label="Food name" error={form.formState.errors.name?.message}>
          <TextInput {...form.register("name")} placeholder="Charcoal Chicken Supreme" />
        </Field>
        <Field label="Category" error={form.formState.errors.category_id?.message}>
          <Select {...form.register("category_id")}>
            <option value="">Select category</option>
            {categories?.map((category) => (
              <option key={category.id} value={category.id}>{category.name}</option>
            ))}
          </Select>
        </Field>
        <Field label="Price" error={form.formState.errors.price?.message}>
          <TextInput {...form.register("price")} inputMode="decimal" placeholder="9800" />
        </Field>
        <Field label="Prep time (minutes)" error={form.formState.errors.preparation_time_minutes?.message}>
          <TextInput {...form.register("preparation_time_minutes")} inputMode="numeric" placeholder="15" />
        </Field>
        <Field label="Availability" error={form.formState.errors.is_available?.message}>
          <Select {...form.register("is_available")}>
            <option value="true">On</option>
            <option value="false">Off</option>
          </Select>
        </Field>
        <div className="sm:col-span-2">
          <Field label="Description" error={form.formState.errors.description?.message}>
            <TextArea {...form.register("description")} placeholder="Describe the dish, texture, sides, and flavor..." />
          </Field>
        </div>
        <div className="sm:col-span-2">
          <Field label="Food image">
            <TextInput type="file" accept="image/*" onChange={onSelectImage} />
            <p className="text-xs text-muted-foreground">
              {selectedImageName || existingFood?.image_url ? (selectedImageName || "Current image already uploaded") : "No image selected yet."}
            </p>
          </Field>
        </div>
        <div className="sm:col-span-2 flex gap-3">
          <Button disabled={isSubmitting}>{isSubmitting ? "Saving..." : "Save food"}</Button>
          <Link to="/admin/foods">
            <Button type="button" variant="outline">Cancel</Button>
          </Link>
        </div>
      </form>
    </Card>
  );
}

export function AdminOrdersPage() {
  const { data: orders } = useOrders();
  return (
    <div className="space-y-6">
      <SectionHeading title="Orders" />
      <DataTable
        columns={["Order", "Date", "Status", "Payment", "Amount", "Action"]}
        rows={(orders ?? []).map((order) => [
          <span className="font-medium">{order.order_number}</span>,
          formatDate(order.created_at),
          <Badge>{order.status.replace(/_/g, " ")}</Badge>,
          <Badge tone={order.payment_status === "SUCCESSFUL" ? "success" : "warning"}>{order.payment_status}</Badge>,
          formatCurrency(order.total),
          <Link to={`/admin/orders/${order.id}`}><Button variant="outline" size="sm">Open</Button></Link>,
        ])}
      />
    </div>
  );
}

export function AdminOrderDetailsPage() {
  const { data: orders } = useOrders();
  const order = orders?.[0];

  if (!order) {
    return <EmptyState title="No order selected" description="Order details will appear here once available." />;
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
        <SectionHeading title="Delivery assignment" description="Assign a rider or review the current dispatch state." />
        <div className="mt-6 space-y-4">
          {demoDeliveryOrders.map((delivery) => (
            <div key={delivery.id} className="rounded-2xl border border-border p-4">
              <p className="font-medium">Delivery #{delivery.id}</p>
              <p className="mt-2 text-sm text-muted-foreground">{delivery.status.replace(/_/g, " ")}</p>
            </div>
          ))}
          <AppDialog
            title="Assign delivery"
            description="Select a rider to assign to this delivery."
            trigger={<Button className="w-full">Assign rider</Button>}
          >
            <div className="space-y-4">
              <Select>
                <option>Choose delivery personnel</option>
                <option>James Okoro</option>
                <option>Peter Adewale</option>
              </Select>
              <Button className="w-full">Confirm assignment</Button>
            </div>
          </AppDialog>
        </div>
      </Card>
    </div>
  );
}

export function CustomersPage() {
  const { data: profile } = useProfile();
  const rows = useMemo(
    () => [
      [profile?.first_name ?? "Amara", profile?.email ?? "amara@example.com", profile?.phone ?? "+234...", "12", <Badge tone="success">Active</Badge>],
      ["Kunle", "kunle@example.com", "+2348098765432", "8", <Badge tone="success">Active</Badge>],
      ["Tosin", "tosin@example.com", "+2348011122233", "5", <Badge tone="warning">New</Badge>],
    ],
    [profile],
  );

  return (
    <div className="space-y-6">
      <SectionHeading title="Customers" />
      <DataTable columns={["Name", "Email", "Phone", "Orders", "Status"]} rows={rows} />
    </div>
  );
}

export function DeliveryPersonnelPage() {
  return (
    <div className="space-y-6">
      <SectionHeading title="Delivery Personnel" />
      <DataTable
        columns={["Name", "Phone", "Status", "Deliveries"]}
        rows={[
          ["James Okoro", "+2348034567890", <Badge tone="success">Active</Badge>, "120"],
          ["Peter Adewale", "+2348012349988", <Badge tone="warning">On route</Badge>, "98"],
          ["Samuel Brown", "+2348065432109", <Badge tone="success">Active</Badge>, "78"],
        ]}
      />
    </div>
  );
}

export function ReportsPage() {
  return (
    <div className="grid gap-6 xl:grid-cols-2">
      <RevenueChartCard />
      <Card className="p-6">
        <SectionHeading title="Order analytics" />
        <div className="mt-6 grid gap-4">
          {[
            { icon: <DollarSign className="h-5 w-5" />, title: "Average order value", value: formatCurrency(3672) },
            { icon: <Package className="h-5 w-5" />, title: "Orders this week", value: "284" },
            { icon: <Users className="h-5 w-5" />, title: "Returning customers", value: "63%" },
            { icon: <Bike className="h-5 w-5" />, title: "On-time delivery", value: "91%" },
          ].map((item) => (
            <div key={item.title} className="flex items-center gap-4 rounded-2xl border border-border p-4">
              <div className="rounded-2xl bg-primary/10 p-3 text-primary">{item.icon}</div>
              <div>
                <p className="text-sm text-muted-foreground">{item.title}</p>
                <p className="text-lg font-semibold">{item.value}</p>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}

export function RevenueAnalyticsPage() {
  return <ReportsPage />;
}

export function AdminNotificationsPage() {
  return (
    <div className="space-y-6">
      <SectionHeading title="Notifications" />
      <div className="grid gap-4">
        {[
          ["Kitchen queue spike", "12 more orders than projected in the last 30 minutes.", "warning"],
          ["Payment reconciliation complete", "Daily payment sync closed successfully.", "success"],
          ["Rider reassignment needed", "Order BM12456789 needs a new delivery person.", "danger"],
        ].map(([title, copy, tone]) => (
          <Card key={title} className="p-5">
            <div className="flex items-center justify-between gap-4">
              <div>
                <h3 className="font-semibold">{title}</h3>
                <p className="mt-2 text-sm text-muted-foreground">{copy}</p>
              </div>
              <Badge tone={tone as "warning" | "success" | "danger"}>{tone}</Badge>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}

export function AdminSettingsPage() {
  return (
    <div className="grid gap-4 xl:grid-cols-2">
      {[
        ["Kitchen SLA alerts", "Notify admins when prep times exceed threshold."],
        ["Automatic rider suggestions", "Prepare dispatch recommendations when delivery demand rises."],
        ["Revenue digest", "Email summary of daily order and revenue performance."],
        ["Catalog publishing controls", "Require admin approval before food edits go live."],
      ].map(([title, copy]) => (
        <Card key={title} className="p-6">
          <h3 className="font-semibold">{title}</h3>
          <p className="mt-2 text-sm text-muted-foreground">{copy}</p>
          <Button className="mt-5" variant="outline">Manage</Button>
        </Card>
      ))}
    </div>
  );
}

function RevenueChartCard() {
  const bars = [24, 48, 38, 62, 40, 72, 55, 68, 49, 58, 64, 80];
  return (
    <Card className="p-6">
      <SectionHeading title="Revenue Overview" />
      <div className="mt-8 grid h-72 grid-cols-12 items-end gap-3">
        {bars.map((bar, index) => (
          <div key={index} className="flex h-full flex-col justify-end gap-3">
            <div className="rounded-t-2xl bg-[linear-gradient(180deg,rgba(194,154,76,0.82),rgba(99,18,34,0.92))]" style={{ height: `${bar}%` }} />
            <span className="text-center text-xs text-muted-foreground">{index + 1}</span>
          </div>
        ))}
      </div>
    </Card>
  );
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
