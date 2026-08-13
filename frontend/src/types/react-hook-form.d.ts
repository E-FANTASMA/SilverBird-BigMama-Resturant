declare module "react-hook-form" {
  export interface UseFormReturn<TFieldValues = Record<string, unknown>> {
    register: (name: keyof TFieldValues | string) => Record<string, unknown>;
    watch: <TName extends keyof TFieldValues | string>(name: TName) => TName extends keyof TFieldValues
      ? TFieldValues[TName]
      : unknown;
    setValue: <TName extends keyof TFieldValues | string>(
      name: TName,
      value: TName extends keyof TFieldValues ? TFieldValues[TName] : unknown,
      options?: { shouldDirty?: boolean; shouldValidate?: boolean; shouldTouch?: boolean },
    ) => void;
    handleSubmit: (
      onValid: (values: TFieldValues) => void | Promise<void>,
    ) => (event?: unknown) => void | Promise<void>;
    formState: {
      errors: Record<string, { message?: string }>;
    };
  }

  export function useForm<TFieldValues = Record<string, unknown>>(options?: unknown): UseFormReturn<TFieldValues>;
}
