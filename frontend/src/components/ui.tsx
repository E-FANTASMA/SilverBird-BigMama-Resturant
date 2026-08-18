import * as Dialog from "@radix-ui/react-dialog";
import { cva, type VariantProps } from "class-variance-authority";
import {
  AlertCircle,
  LoaderCircle,
  Search,
  SlidersHorizontal,
  Sparkles,
  X,
} from "lucide-react";
import type {
  ButtonHTMLAttributes,
  ForwardedRef,
  HTMLAttributes,
  InputHTMLAttributes,
  ReactNode,
  TextareaHTMLAttributes,
} from "react";
import { forwardRef } from "react";
import { cn } from "@/lib/utils";
export { cn };

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 rounded-2xl text-sm font-semibold transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground shadow-soft hover:-translate-y-0.5 hover:shadow-float",
        secondary: "bg-secondary text-secondary-foreground hover:bg-secondary/80",
        outline: "border border-border bg-white hover:bg-secondary/50",
        ghost: "hover:bg-primary/5 hover:text-primary",
        danger: "bg-danger text-white hover:bg-danger/90",
      },
      size: {
        default: "h-11 px-5",
        sm: "h-9 px-3 text-xs",
        lg: "h-12 px-6",
        icon: "h-11 w-11",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  },
);

export function Button({
  className,
  variant,
  size,
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & VariantProps<typeof buttonVariants>) {
  return <button className={cn(buttonVariants({ variant, size }), className)} {...props} />;
}

export function Card({ className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn("rounded-3xl border border-white/60 bg-card shadow-soft backdrop-blur-sm", className)}
      {...props}
    />
  );
}

export function SectionHeading({
  eyebrow,
  title,
  description,
  action,
}: {
  eyebrow?: string;
  title: string;
  description?: string;
  action?: ReactNode;
}) {
  return (
    <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
      <div className="space-y-2">
        {eyebrow ? <p className="text-xs font-semibold uppercase tracking-[0.28em] text-primary/70">{eyebrow}</p> : null}
        <div className="space-y-1">
          <h2 className="text-2xl font-bold tracking-tight text-foreground sm:text-3xl">{title}</h2>
          {description ? <p className="max-w-2xl text-sm text-muted-foreground sm:text-base">{description}</p> : null}
        </div>
      </div>
      {action}
    </div>
  );
}

export function Badge({
  children,
  tone = "default",
}: {
  children: ReactNode;
  tone?: "default" | "success" | "warning" | "danger";
}) {
  const classes = {
    default: "bg-primary/10 text-primary",
    success: "bg-success/10 text-success",
    warning: "bg-warning/12 text-warning",
    danger: "bg-danger/10 text-danger",
  };

  return (
    <span className={cn("inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold", classes[tone])}>
      {children}
    </span>
  );
}

export const TextInput = forwardRef(function TextInput(
  {
    className,
    icon,
    ...props
  }: InputHTMLAttributes<HTMLInputElement> & { icon?: ReactNode },
  ref: ForwardedRef<HTMLInputElement>,
) {
  return (
    <div className="relative">
      {icon ? <div className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-muted-foreground">{icon}</div> : null}
      <input
        ref={ref}
        className={cn(
          "h-12 w-full rounded-2xl border border-input bg-white px-4 text-sm outline-none transition focus:border-primary focus:ring-4 focus:ring-primary/10",
          icon ? "pl-11" : "",
          className,
        )}
        {...props}
      />
    </div>
  );
});

export const TextArea = forwardRef(function TextArea(
  props: TextareaHTMLAttributes<HTMLTextAreaElement>,
  ref: ForwardedRef<HTMLTextAreaElement>,
) {
  return (
    <textarea
      ref={ref}
      className="min-h-28 w-full rounded-2xl border border-input bg-white px-4 py-3 text-sm outline-none transition focus:border-primary focus:ring-4 focus:ring-primary/10"
      {...props}
    />
  );
});

export const Select = forwardRef(function Select(
  props: React.SelectHTMLAttributes<HTMLSelectElement>,
  ref: ForwardedRef<HTMLSelectElement>,
) {
  return (
    <select
      ref={ref}
      className="h-12 w-full rounded-2xl border border-input bg-white px-4 text-sm outline-none transition focus:border-primary focus:ring-4 focus:ring-primary/10"
      {...props}
    />
  );
});

export function FoodCard({
  image,
  title,
  description,
  price,
  meta,
  action,
}: {
  image?: string | null;
  title: string;
  description?: string | null;
  price: string;
  meta?: string;
  action?: ReactNode;
}) {
  return (
    <Card className="overflow-hidden rounded-[2rem]">
      <div className="aspect-[4/3] overflow-hidden bg-secondary">
        <img
          src={image ?? "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=900&q=80"}
          alt={title}
          className="h-full w-full object-cover transition duration-500 hover:scale-105"
        />
      </div>
      <div className="space-y-4 p-6">
        <div className="flex items-start justify-between gap-4">
          <div className="space-y-2">
            <h3 className="text-lg font-semibold leading-tight text-foreground">{title}</h3>
            {description ? <p className="line-clamp-2 text-sm leading-6 text-muted-foreground">{description}</p> : null}
          </div>
          <Badge>{price}</Badge>
        </div>
        <div className="flex items-center justify-between gap-3 border-t border-border/60 pt-4">
          <p className="text-xs font-medium uppercase tracking-[0.16em] text-muted-foreground">{meta}</p>
          {action}
        </div>
      </div>
    </Card>
  );
}

export function StatCard({
  label,
  value,
  delta,
}: {
  label: string;
  value: string;
  delta?: string;
}) {
  return (
    <Card className="min-w-0 p-5">
      <p className="text-sm text-muted-foreground">{label}</p>
      <div className="mt-4 flex items-end justify-between gap-3">
        <p className="min-w-0 break-words text-xl font-bold leading-tight text-foreground sm:text-2xl">{value}</p>
        {delta ? <Badge tone="success">{delta}</Badge> : null}
      </div>
    </Card>
  );
}

export function SearchInput(props: InputHTMLAttributes<HTMLInputElement>) {
  return <TextInput icon={<Search className="h-4 w-4" />} placeholder="Search meals, orders, customers..." {...props} />;
}

export function FilterChip({
  label,
  active,
  onClick,
}: {
  label: string;
  active?: boolean;
  onClick?: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        "rounded-full border px-4 py-2 text-sm font-medium transition",
        active ? "border-primary bg-primary text-white" : "border-border bg-white text-muted-foreground hover:border-primary/40",
      )}
    >
      {label}
    </button>
  );
}

export function Skeleton({ className }: { className?: string }) {
  return <div className={cn("animate-pulse rounded-2xl bg-secondary", className)} />;
}

export function LoadingState({ label = "Loading..." }: { label?: string }) {
  return (
    <div className="flex min-h-[220px] flex-col items-center justify-center gap-3 rounded-3xl border border-dashed border-border bg-white/70 p-8 text-center">
      <LoaderCircle className="h-8 w-8 animate-spin text-primary" />
      <p className="text-sm text-muted-foreground">{label}</p>
    </div>
  );
}

export function EmptyState({
  title,
  description,
  action,
}: {
  title: string;
  description: string;
  action?: ReactNode;
}) {
  return (
    <Card className="flex min-h-[240px] flex-col items-center justify-center gap-4 p-8 text-center">
      <div className="rounded-full bg-secondary p-4 text-primary">
        <Sparkles className="h-6 w-6" />
      </div>
      <div className="space-y-2">
        <h3 className="text-lg font-semibold">{title}</h3>
        <p className="max-w-md text-sm text-muted-foreground">{description}</p>
      </div>
      {action}
    </Card>
  );
}

export function ErrorState({
  title = "Something went wrong",
  description = "We couldn't load this section right now.",
  action,
}: {
  title?: string;
  description?: string;
  action?: ReactNode;
}) {
  return (
    <Card className="flex min-h-[220px] flex-col items-center justify-center gap-4 border-danger/20 p-8 text-center">
      <div className="rounded-full bg-danger/10 p-4 text-danger">
        <AlertCircle className="h-6 w-6" />
      </div>
      <div className="space-y-2">
        <h3 className="text-lg font-semibold">{title}</h3>
        <p className="max-w-md text-sm text-muted-foreground">{description}</p>
      </div>
      {action}
    </Card>
  );
}

export function DataTable({
  columns,
  rows,
}: {
  columns: string[];
  rows: ReactNode[][];
}) {
  return (
    <Card className="overflow-hidden">
      <div className="overflow-x-auto">
        <table className="min-w-full text-left">
          <thead className="bg-secondary/70 text-xs uppercase tracking-[0.18em] text-muted-foreground">
            <tr>
              {columns.map((column) => (
                <th key={column} className="px-6 py-4 font-semibold">
                  {column}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-border/70">
            {rows.map((row, index) => (
              <tr key={index} className="bg-white/90">
                {row.map((cell, cellIndex) => (
                  <td key={cellIndex} className="px-6 py-4 text-sm">
                    {cell}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
}

export function Pagination({
  page,
  pageCount,
  onChange,
}: {
  page: number;
  pageCount: number;
  onChange: (page: number) => void;
}) {
  const pages = Array.from({ length: pageCount }, (_, index) => index + 1);
  return (
    <div className="flex items-center gap-2">
      {pages.map((item) => (
        <Button
          key={item}
          variant={page === item ? "default" : "outline"}
          size="sm"
          onClick={() => onChange(item)}
        >
          {item}
        </Button>
      ))}
    </div>
  );
}

export function AppDialog({
  title,
  description,
  trigger,
  children,
}: {
  title: string;
  description?: string;
  trigger: ReactNode;
  children: ReactNode;
}) {
  return (
    <Dialog.Root>
      <Dialog.Trigger asChild>{trigger}</Dialog.Trigger>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 z-50 bg-foreground/30 backdrop-blur-sm" />
        <Dialog.Content className="fixed left-1/2 top-1/2 z-50 w-[calc(100%-2rem)] max-w-2xl -translate-x-1/2 -translate-y-1/2 rounded-3xl border border-white/60 bg-white p-6 shadow-float">
          <div className="mb-5 flex items-start justify-between gap-4">
            <div className="space-y-1">
              <Dialog.Title className="text-xl font-semibold">{title}</Dialog.Title>
              {description ? <Dialog.Description className="text-sm text-muted-foreground">{description}</Dialog.Description> : null}
            </div>
            <Dialog.Close asChild>
              <button className="rounded-full p-2 text-muted-foreground transition hover:bg-secondary hover:text-foreground">
                <X className="h-4 w-4" />
              </button>
            </Dialog.Close>
          </div>
          {children}
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}

export function AnimatedList({ children }: { children: ReactNode }) {
  return <div className="animate-fade-up space-y-4">{children}</div>;
}

export function FilterButton() {
  return (
    <Button variant="outline">
      <SlidersHorizontal className="h-4 w-4" />
      Filters
    </Button>
  );
}
