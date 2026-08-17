import { Clock3, MapPinned, PhoneCall, Route } from "lucide-react";
import type { ReactNode } from "react";
import { Link, useParams } from "react-router-dom";
import { useDeliveryContact, useDeliveryOrders, useProfile } from "@/api/hooks";
import { formatDate } from "@/lib/format";
import { Badge, Button, Card, EmptyState, SectionHeading, StatCard } from "@/components/ui";

export function DeliveryDashboardPage() {
  const { data: deliveries } = useDeliveryOrders();

  return (
    <div className="space-y-6">
      <SectionHeading title="Delivery Dashboard" />
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Assigned now" value={`${deliveries?.length ?? 0}`} />
        <StatCard label="In transit" value={`${deliveries?.filter((item) => item.status === "IN_TRANSIT").length ?? 0}`} />
        <StatCard label="Delivered today" value="14" />
        <StatCard label="Avg. completion" value="28 mins" />
      </div>
    </div>
  );
}

export function AssignedOrdersPage() {
  const { data: deliveries } = useDeliveryOrders();

  if (!deliveries?.length) {
    return <EmptyState title="No assigned deliveries" description="New assignments will appear here as soon as dispatch creates them." />;
  }

  return (
    <div className="space-y-6">
      <SectionHeading title="Assigned Orders" />
      <div className="grid gap-4">
        {deliveries.map((delivery) => (
          <Card key={delivery.id} className="p-5">
            <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
              <div>
                <div className="flex items-center gap-3">
                  <h3 className="font-semibold">Delivery {delivery.id}</h3>
                  <Badge>{delivery.status.replace(/_/g, " ")}</Badge>
                </div>
                <p className="mt-2 text-sm text-muted-foreground">
                  ETA {delivery.estimated_delivery_time ? formatDate(delivery.estimated_delivery_time) : "Pending"}
                </p>
              </div>
              <Link to={`/delivery/orders/${delivery.id}`}>
                <Button variant="outline">Open details</Button>
              </Link>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}

export function DeliveryDetailsPage() {
  const { deliveryId = "" } = useParams();
  const { data: contact } = useDeliveryContact(deliveryId);

  return (
    <div className="grid gap-6 xl:grid-cols-[1fr_0.9fr]">
      <Card className="p-6">
        <SectionHeading title="Delivery Details" />
        <div className="mt-6 grid gap-4">
          <Detail icon={<PhoneCall className="h-5 w-5" />} label="Customer" value={contact?.customer_name ?? "Unavailable"} />
          <Detail icon={<PhoneCall className="h-5 w-5" />} label="Phone" value={contact?.customer_phone ?? "Unavailable"} />
          <Detail icon={<MapPinned className="h-5 w-5" />} label="Address" value={contact?.delivery_address ?? "Unavailable"} />
          <Detail icon={<Route className="h-5 w-5" />} label="City / State" value={`${contact?.city ?? "-"}, ${contact?.state ?? "-"}`} />
        </div>
      </Card>
      <Card className="p-6">
        <SectionHeading title="Rider actions" description="Update the delivery status as you progress." />
        <div className="mt-6 flex flex-col gap-3">
          <Button>Mark as picked up</Button>
          <Button variant="outline">Mark in transit</Button>
          <Button variant="secondary">Mark delivered</Button>
        </div>
      </Card>
    </div>
  );
}

export function DeliveryHistoryPage() {
  const { data: deliveries } = useDeliveryOrders();
  return (
    <div className="space-y-6">
      <SectionHeading title="Delivery History" />
      <div className="grid gap-4">
        {deliveries?.map((delivery) => (
          <Card key={delivery.id} className="p-5">
            <div className="flex items-center justify-between gap-3">
              <div>
                <h3 className="font-semibold">{delivery.id}</h3>
                <p className="mt-2 text-sm text-muted-foreground">{delivery.delivered_at ? formatDate(delivery.delivered_at) : "Pending completion"}</p>
              </div>
              <Badge>{delivery.status.replace(/_/g, " ")}</Badge>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}

export function DeliveryProfilePage() {
  const { data: profile } = useProfile();
  return (
    <Card className="max-w-3xl p-6">
      <SectionHeading title="Rider Profile" />
      <div className="mt-6 grid gap-4 sm:grid-cols-2">
        <Detail icon={<PhoneCall className="h-5 w-5" />} label="Name" value={`${profile?.first_name ?? ""} ${profile?.last_name ?? ""}`} />
        <Detail icon={<PhoneCall className="h-5 w-5" />} label="Phone" value={profile?.phone ?? "Unavailable"} />
        <Detail icon={<Clock3 className="h-5 w-5" />} label="Status" value={profile?.is_active ? "Active" : "Inactive"} />
        <Detail icon={<Route className="h-5 w-5" />} label="Role" value="Delivery Personnel" />
      </div>
    </Card>
  );
}

function Detail({ icon, label, value }: { icon: ReactNode; label: string; value: string }) {
  return (
    <div className="flex items-start gap-4 rounded-2xl border border-border p-4">
      <div className="rounded-2xl bg-primary/10 p-3 text-primary">{icon}</div>
      <div>
        <p className="text-sm text-muted-foreground">{label}</p>
        <p className="mt-1 font-medium">{value}</p>
      </div>
    </div>
  );
}
