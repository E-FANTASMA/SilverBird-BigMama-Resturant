declare module "react-hook-form" {
  export interface UseFormReturn<TFieldValues = Record<string, unknown>> {
    register: (name: keyof TFieldValues | string) => Record<string, unknown>;
    handleSubmit: (
      onValid: (values: TFieldValues) => void | Promise<void>,
    ) => (event?: unknown) => void | Promise<void>;
    formState: {
      errors: Record<string, { message?: string }>;
    };
  }

  export function useForm<TFieldValues = Record<string, unknown>>(options?: unknown): UseFormReturn<TFieldValues>;
}
