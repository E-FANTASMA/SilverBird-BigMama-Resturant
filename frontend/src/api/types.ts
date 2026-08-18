export type Role = "CUSTOMER" | "ADMIN" | "DELIVERY_PERSONNEL";
export type OrderType = "DINE_IN" | "PICKUP" | "DELIVERY";
export type OrderStatus =
  | "PENDING"
  | "CONFIRMED"
  | "PREPARING"
  | "READY"
  | "OUT_FOR_DELIVERY"
  | "DELIVERED"
  | "CANCELLED";
export type PaymentStatus = "PENDING" | "SUCCESSFUL" | "FAILED" | "REFUNDED";
export type DeliveryStatus = "ASSIGNED" | "PICKED_UP" | "IN_TRANSIT" | "DELIVERED" | "FAILED";
export type NotificationType = "ORDER" | "PAYMENT" | "DELIVERY" | "SYSTEM";

export interface Timestamped {
  id: string;
  created_at: string;
  updated_at: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface Category extends Timestamped {
  name: string;
  slug: string;
  description: string | null;
  sort_order: number;
}

export interface Food extends Timestamped {
  category_id: string;
  name: string;
  slug: string;
  description: string | null;
  price: number;
  image_url: string | null;
  image_path: string | null;
  is_available: boolean;
  preparation_time_minutes: number | null;
}

export interface FoodPayload {
  category_id: string;
  name: string;
  description: string | null;
  price: number;
  is_available: boolean;
  preparation_time_minutes: number | null;
}

export interface CartItem extends Timestamped {
  cart_id: string;
  food_item_id: string;
  food_name: string;
  quantity: number;
  unit_price: number;
  subtotal: number;
}

export interface Cart extends Timestamped {
  user_id: string;
  items: CartItem[];
  total_items: number;
  subtotal: number;
  delivery_fee: number;
  tax_amount: number;
  discount_amount: number;
  grand_total: number;
  currency: string;
}

export interface OrderItem {
  id: string;
  food_item_id: string;
  food_name_snapshot: string;
  quantity: number;
  unit_price: number;
  subtotal: number;
}

export interface Order extends Timestamped {
  user_id: string;
  order_number: string;
  order_type: OrderType;
  delivery_address_id: string | null;
  status: OrderStatus;
  subtotal: number;
  delivery_fee: number;
  delivery_distance_km: number | null;
  total: number;
  notes: string | null;
  table_number: string | null;
  scheduled_pickup_time: string | null;
  payment_status: PaymentStatus;
  items: OrderItem[];
}

export interface Address extends Timestamped {
  user_id: string;
  label: string;
  address: string;
  city: string;
  state: string;
  phone: string;
  latitude: number | null;
  longitude: number | null;
  is_default: boolean;
}

export interface UserProfile extends Timestamped {
  role_id: string;
  first_name: string;
  last_name: string;
  email: string;
  phone: string | null;
  is_verified: boolean;
  is_active: boolean;
}

export interface NotificationDelivery extends Timestamped {
  notification_id: string;
  channel: "IN_APP" | "EMAIL" | "SMS";
  recipient: string;
  status: "PENDING" | "SENT" | "FAILED" | "DELIVERED";
  provider: string | null;
  provider_message_id: string | null;
  error_message: string | null;
}

export interface NotificationItem extends Timestamped {
  user_id: string;
  title: string;
  message: string;
  type: NotificationType;
  is_read: boolean;
  deliveries: NotificationDelivery[];
}

export interface PaymentInitializeResponse {
  order_id: string;
  reference: string;
  authorization_url: string;
  amount: number;
  status: PaymentStatus;
}

export interface PaymentVerifyResponse {
  order_id: string;
  reference: string;
  status: PaymentStatus;
  gateway_response: string | null;
  paid_at: string | null;
}

export interface DeliveryOrder extends Timestamped {
  order_id: string;
  delivery_personnel_id: string;
  delivery_address_id: string;
  status: DeliveryStatus;
  estimated_delivery_time: string | null;
  picked_up_at: string | null;
  delivered_at: string | null;
}

export interface DeliveryContact {
  order_id: string;
  customer_name: string;
  customer_phone: string | null;
  delivery_address: string | null;
  city: string | null;
  state: string | null;
}

export interface DashboardSummary {
  pending_orders: number;
  total_orders: number;
  total_customers: number;
  total_revenue: number;
}
