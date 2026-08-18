import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { api } from "@/api/client";
import type {
  Address,
  AuthResponse,
  Cart,
  Category,
  DashboardSummary,
  DeliveryContact,
  DeliveryOrder,
  Food,
  FoodPayload,
  NotificationItem,
  Order,
  PaymentInitializeResponse,
  PaymentVerifyResponse,
  UserProfile,
} from "@/api/types";
import {
  demoAddresses,
  demoCategories,
  demoDeliveryContact,
  demoDeliveryOrders,
  demoFoods,
  demoNotifications,
  demoOrders,
  demoProfile,
} from "@/lib/mock";
import { clearSession, saveSession } from "@/lib/session";

export const queryKeys = {
  categories: ["categories"],
  foods: ["foods"],
  food: (id: string) => ["foods", id],
  cart: ["cart"],
  orders: ["orders"],
  order: (id: string) => ["orders", id],
  addresses: ["addresses"],
  profile: ["profile"],
  notifications: ["notifications"],
  adminDashboard: ["admin-dashboard"],
  deliveryOrders: ["delivery-orders"],
  deliveryContact: (id: string) => ["delivery-contact", id],
};

function withFallback<T>(promise: Promise<T>, fallback: T) {
  return promise.catch(() => fallback);
}

function getApiErrorMessage(error: unknown, fallback: string) {
  if (typeof error === "object" && error !== null) {
    const maybeResponse = (error as { response?: { data?: { detail?: unknown; message?: unknown } } }).response;
    const detail = maybeResponse?.data?.detail;
    const message = maybeResponse?.data?.message;

    if (typeof detail === "string" && detail.trim()) {
      return detail;
    }
    if (Array.isArray(detail) && detail.length > 0) {
      const first = detail[0] as { msg?: unknown } | undefined;
      if (typeof first?.msg === "string" && first.msg.trim()) {
        return first.msg;
      }
    }
    if (typeof message === "string" && message.trim()) {
      return message;
    }
  }

  return fallback;
}

export function useCategories() {
  return useQuery({
    queryKey: queryKeys.categories,
    queryFn: () => api.get<Category[]>("/categories").then((r) => r.data),
  });
}

export function useFoods() {
  return useQuery({
    queryKey: queryKeys.foods,
    queryFn: () => api.get<Food[]>("/foods").then((r) => r.data),
  });
}

export function useFood(foodId?: string) {
  return useQuery({
    enabled: Boolean(foodId),
    queryKey: queryKeys.food(foodId ?? ""),
    queryFn: () => api.get<Food>(`/foods/${foodId}`).then((r) => r.data),
  });
}

export function useCreateFood() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: FoodPayload) => api.post<Food>("/foods", payload).then((r) => r.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.foods });
      toast.success("Food created");
    },
    onError: (error) => toast.error(getApiErrorMessage(error, "Could not create food")),
  });
}

export function useUpdateFood() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: { foodId: string; data: Partial<FoodPayload> }) =>
      api.patch<Food>(`/foods/${payload.foodId}`, payload.data).then((r) => r.data),
    onSuccess: (food) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.foods });
      queryClient.invalidateQueries({ queryKey: queryKeys.food(food.id) });
      toast.success("Food updated");
    },
    onError: (error) => toast.error(getApiErrorMessage(error, "Could not update food")),
  });
}

export function useUploadFoodImage() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ foodId, file }: { foodId: string; file: File }) => {
      const formData = new FormData();
      formData.append("image", file);
      return api.post<Food>(`/foods/${foodId}/image`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      }).then((r) => r.data);
    },
    onSuccess: (food) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.foods });
      queryClient.invalidateQueries({ queryKey: queryKeys.food(food.id) });
      toast.success("Food image uploaded");
    },
    onError: (error) => toast.error(getApiErrorMessage(error, "Could not upload image")),
  });
}

export function useCart() {
  return useQuery({
    queryKey: queryKeys.cart,
    queryFn: () =>
      withFallback(
        api.get<Cart>("/cart").then((r) => r.data),
        {
          id: "cart-demo",
          user_id: "user-1",
          items: [],
          total_items: 0,
          subtotal: 0,
          delivery_fee: 0,
          tax_amount: 0,
          discount_amount: 0,
          grand_total: 0,
          currency: "NGN",
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        },
      ),
  });
}

export function useOrders() {
  return useQuery({
    queryKey: queryKeys.orders,
    queryFn: () => withFallback(api.get<Order[]>("/orders").then((r) => r.data), demoOrders),
  });
}

export function useOrder(orderId?: string) {
  return useQuery({
    enabled: Boolean(orderId),
    queryKey: queryKeys.order(orderId ?? ""),
    queryFn: () =>
      withFallback(
        api.get<Order>(`/orders/${orderId}`).then((r) => r.data),
        demoOrders.find((order) => order.id === orderId) ?? demoOrders[0],
      ),
  });
}

export function useAddresses() {
  return useQuery({
    queryKey: queryKeys.addresses,
    queryFn: () => withFallback(api.get<Address[]>("/addresses").then((r) => r.data), demoAddresses),
  });
}

export function useCreateAddress() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: Record<string, unknown>) => api.post<Address>("/addresses", payload).then((r) => r.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.addresses });
      queryClient.invalidateQueries({ queryKey: queryKeys.cart });
      toast.success("Address saved");
    },
    onError: (error) => toast.error(getApiErrorMessage(error, "Could not save address")),
  });
}

export function useUpdateAddress() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: { addressId: string; data: Record<string, unknown> }) =>
      api.patch<Address>(`/addresses/${payload.addressId}`, payload.data).then((r) => r.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.addresses });
      queryClient.invalidateQueries({ queryKey: queryKeys.cart });
      toast.success("Address updated");
    },
    onError: (error) => toast.error(getApiErrorMessage(error, "Could not update address")),
  });
}

export function useProfile() {
  return useQuery({
    queryKey: queryKeys.profile,
    queryFn: () => withFallback(api.get<UserProfile>("/profile").then((r) => r.data), demoProfile),
  });
}

export function useNotifications() {
  return useQuery({
    queryKey: queryKeys.notifications,
    queryFn: () =>
      withFallback(api.get<NotificationItem[]>("/notifications").then((r) => r.data), demoNotifications),
  });
}

export function useAdminDashboard() {
  return useQuery({
    queryKey: queryKeys.adminDashboard,
    queryFn: () =>
      withFallback(
        api.get<DashboardSummary>("/admin/dashboard").then((r) => r.data),
        {
          total_orders: 1248,
          total_customers: 856,
          total_revenue: 45800200,
          pending_orders: 32,
        },
      ),
  });
}

export function useDeliveryOrders() {
  return useQuery({
    queryKey: queryKeys.deliveryOrders,
    queryFn: () =>
      withFallback(api.get<DeliveryOrder[]>("/delivery/orders").then((r) => r.data), demoDeliveryOrders),
  });
}

export function useDeliveryContact(deliveryId?: string) {
  return useQuery({
    enabled: Boolean(deliveryId),
    queryKey: queryKeys.deliveryContact(deliveryId ?? ""),
    queryFn: () =>
      withFallback(
        api.get<DeliveryContact>(`/delivery/orders/${deliveryId}/contact`).then((r) => r.data),
        demoDeliveryContact,
      ),
  });
}

export function useLogin() {
  return useMutation({
    mutationFn: async (payload: { email: string; password: string }) => {
      const response = await api.post<AuthResponse>("/auth/login", payload);
      return saveSession({
        accessToken: response.data.access_token,
        refreshToken: response.data.refresh_token,
        tokenType: response.data.token_type,
      });
    },
    onError: (error) => toast.error(getApiErrorMessage(error, "Sign in failed")),
  });
}

export function useRegister() {
  return useMutation({
    mutationFn: async (payload: {
      role: "CUSTOMER" | "DELIVERY_PERSONNEL";
      first_name: string;
      last_name: string;
      email: string;
      phone?: string;
      password: string;
    }) => {
      const response = await api.post<AuthResponse>("/auth/signup", payload);
      return saveSession({
        accessToken: response.data.access_token,
        refreshToken: response.data.refresh_token,
        tokenType: response.data.token_type,
      });
    },
    onError: (error) => toast.error(getApiErrorMessage(error, "Registration failed")),
  });
}

export function useForgotPassword() {
  return useMutation({
    mutationFn: async (payload: { email: string }) => {
      const response = await api.post<{ message: string; reset_token?: string }>("/auth/forgot-password", payload);
      return response.data;
    },
    onSuccess: (data) => toast.success(data.message),
    onError: (error) => toast.error(getApiErrorMessage(error, "Password reset request failed")),
  });
}

export function useResetPassword() {
  return useMutation({
    mutationFn: async (payload: { reset_token: string; password: string; confirm_password: string }) => {
      const response = await api.post<{ message: string }>("/auth/reset-password", payload);
      return response.data;
    },
    onSuccess: (data) => toast.success(data.message),
    onError: (error) => toast.error(getApiErrorMessage(error, "Password reset failed")),
  });
}

export function useLogout() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async () => {
      try {
        const session = JSON.parse(localStorage.getItem("silverbird.session") ?? "null") as
          | { refreshToken?: string }
          | null;
        if (session?.refreshToken) {
          await api.post("/auth/logout", { refresh_token: session.refreshToken });
        }
      } finally {
        clearSession();
        queryClient.clear();
      }
    },
  });
}

export function useAddToCart() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: { food_item_id: string; quantity: number }) =>
      api.post<Cart>("/cart/items", payload).then((r) => r.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.cart });
      toast.success("Added to cart");
    },
    onError: () => toast.error("Could not add item to cart"),
  });
}

export function useUpdateCartItem() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: { itemId: string; quantity: number }) =>
      api.patch<Cart>(`/cart/items/${payload.itemId}`, { quantity: payload.quantity }).then((r) => r.data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: queryKeys.cart }),
  });
}

export function useCreateOrder() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: Record<string, unknown>) => api.post<Order>("/orders", payload).then((r) => r.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.orders });
      queryClient.invalidateQueries({ queryKey: queryKeys.cart });
      toast.success("Order created");
    },
    onError: (error) => toast.error(getApiErrorMessage(error, "Order creation failed")),
  });
}

export function useInitializePayment() {
  return useMutation({
    mutationFn: (orderId: string) =>
      api.post<PaymentInitializeResponse>("/payments/initialize", { order_id: orderId }).then((r) => r.data),
  });
}

export function useVerifyPayment(reference?: string) {
  return useQuery({
    enabled: Boolean(reference),
    queryKey: ["payment-verify", reference],
    queryFn: () =>
      withFallback(
        api.get<PaymentVerifyResponse>(`/payments/verify/${reference}`).then((r) => r.data),
        {
          order_id: demoOrders[0].id,
          reference: reference ?? "demo-ref",
          status: "SUCCESSFUL",
          gateway_response: "Approved",
          paid_at: new Date().toISOString(),
        },
      ),
  });
}
