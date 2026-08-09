import { zodResolver } from "@hookform/resolvers/zod";
import { ArrowRight, Lock, Mail, Phone } from "lucide-react";
import type { ReactNode } from "react";
import { useForm } from "react-hook-form";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { z } from "zod";
import { useForgotPassword, useLogin, useRegister } from "@/api/hooks";
import { useAuth } from "@/auth/auth-store";
import { MarketingShell } from "@/components/layout";
import { Button, Card, TextInput } from "@/components/ui";

const loginSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
});

const registerSchema = z.object({
  first_name: z.string().min(1),
  last_name: z.string().min(1),
  email: z.string().email(),
  phone: z.string().min(8),
  password: z
    .string()
    .min(8)
    .regex(/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\w\s])/, "Use upper, lower, number, and symbol"),
});

const forgotSchema = z.object({
  email: z.string().email(),
});

export function LandingPage() {
  return (
    <MarketingShell>
      <div className="relative overflow-hidden rounded-[2.5rem] border border-white/60 bg-white/55 px-5 py-8 shadow-soft backdrop-blur-sm sm:px-8 lg:px-10">
        <div className="pointer-events-none absolute inset-0 overflow-hidden">
          {[
            "left-[2%] top-[10%] w-24 logo-drift-slow opacity-[0.08]",
            "left-[26%] top-[62%] w-20 logo-drift-medium opacity-[0.07]",
            "left-[48%] top-[8%] w-28 logo-drift-fast opacity-[0.06]",
            "right-[18%] top-[28%] w-24 logo-drift-medium opacity-[0.08]",
            "right-[4%] bottom-[8%] w-32 logo-drift-slow opacity-[0.06]",
            "left-[8%] bottom-[12%] w-16 logo-drift-fast opacity-[0.08]",
          ].map((className, index) => (
            <img
              key={index}
              src="/silverbird-logo.png"
              alt=""
              aria-hidden="true"
              className={`absolute select-none ${className}`}
            />
          ))}
        </div>

        <div className="relative grid min-h-[92vh] items-center gap-8 lg:grid-cols-[1.05fr_0.95fr]">
        <div className="animate-fade-up space-y-6">
          <div className="space-y-4">
            <p className="text-sm font-semibold uppercase tracking-[0.42em] text-primary/70 sm:text-base">
              Silverbird BigMama Restaurant
            </p>
            <h1 className="max-w-2xl text-4xl font-extrabold tracking-tight text-foreground sm:text-6xl">
              Fresh meals, fast ordering, and a restaurant experience that feels as good as the food looks.
            </h1>
          </div>
          <div className="flex flex-col gap-3 sm:flex-row">
            <Link to="/menu">
              <Button size="lg">
                Start Ordering
                <ArrowRight className="h-4 w-4" />
              </Button>
            </Link>
            <Link to="/login">
              <Button variant="outline" size="lg">
                Sign In
              </Button>
            </Link>
          </div>
        </div>

        <div className="relative animate-fade-up">
          <div className="absolute -left-6 top-12 h-40 w-40 rounded-full bg-accent/30 blur-3xl" />
          <Card className="relative overflow-hidden p-3 sm:p-4">
            <div className="relative overflow-hidden rounded-[2rem]">
              <img
                src="/landing-food.jpg"
                alt="Silverbird BigMama food spread"
                className="h-[520px] w-full object-cover"
              />
              <div className="absolute inset-0 bg-[linear-gradient(180deg,rgba(41,15,18,0.04),rgba(41,15,18,0.38))]" />
            </div>
          </Card>
        </div>
        </div>
      </div>
    </MarketingShell>
  );
}

export function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { setSession } = useAuth();
  const login = useLogin();
  const form = useForm<z.infer<typeof loginSchema>>({
    resolver: zodResolver(loginSchema),
    defaultValues: { email: "", password: "" },
  });

  const onSubmit = form.handleSubmit(async (values: z.infer<typeof loginSchema>) => {
    const session = await login.mutateAsync(values);
    setSession(session);
    const role = session.role;
    const from = location.state?.from?.pathname as string | undefined;
    navigate(
      from ??
        (role === "ADMIN"
          ? "/admin/dashboard"
          : role === "DELIVERY_PERSONNEL"
            ? "/delivery/dashboard"
            : "/app/home"),
    );
  });

  return (
    <AuthLayout
      title="Welcome back"
      description="Sign in to continue your Silverbird BigMama experience."
      footer={
        <p className="text-sm text-muted-foreground">
          New here?{" "}
          <Link to="/register" className="font-semibold text-primary">
            Create an account
          </Link>
        </p>
      }
    >
      <form className="space-y-4" onSubmit={onSubmit}>
        <Field label="Email" error={form.formState.errors.email?.message}>
          <TextInput icon={<Mail className="h-4 w-4" />} {...form.register("email")} placeholder="name@example.com" />
        </Field>
        <Field label="Password" error={form.formState.errors.password?.message}>
          <TextInput icon={<Lock className="h-4 w-4" />} type="password" {...form.register("password")} placeholder="Enter your password" />
        </Field>
        <div className="flex justify-end">
          <Link to="/forgot-password" className="text-sm font-medium text-primary">
            Forgot password?
          </Link>
        </div>
        <Button className="w-full" size="lg" disabled={login.isPending}>
          {login.isPending ? "Signing in..." : "Sign in"}
        </Button>
      </form>
    </AuthLayout>
  );
}

export function RegisterPage() {
  const navigate = useNavigate();
  const { setSession } = useAuth();
  const register = useRegister();
  const form = useForm<z.infer<typeof registerSchema>>({
    resolver: zodResolver(registerSchema),
    defaultValues: { first_name: "", last_name: "", email: "", phone: "", password: "" },
  });

  const onSubmit = form.handleSubmit(async (values: z.infer<typeof registerSchema>) => {
    const session = await register.mutateAsync(values);
    setSession(session);
    navigate("/app/home");
  });

  return (
    <AuthLayout
      title="Create your account"
      description="Join the premium dining platform in a few quick steps."
      footer={
        <p className="text-sm text-muted-foreground">
          Already have an account?{" "}
          <Link to="/login" className="font-semibold text-primary">
            Sign in
          </Link>
        </p>
      }
    >
      <form className="grid gap-4" onSubmit={onSubmit}>
        <div className="grid gap-4 sm:grid-cols-2">
          <Field label="First name" error={form.formState.errors.first_name?.message}>
            <TextInput {...form.register("first_name")} placeholder="Amara" />
          </Field>
          <Field label="Last name" error={form.formState.errors.last_name?.message}>
            <TextInput {...form.register("last_name")} placeholder="Okafor" />
          </Field>
        </div>
        <Field label="Email" error={form.formState.errors.email?.message}>
          <TextInput icon={<Mail className="h-4 w-4" />} {...form.register("email")} placeholder="name@example.com" />
        </Field>
        <Field label="Phone" error={form.formState.errors.phone?.message}>
          <TextInput icon={<Phone className="h-4 w-4" />} {...form.register("phone")} placeholder="+2348012345678" />
        </Field>
        <Field label="Password" error={form.formState.errors.password?.message}>
          <TextInput icon={<Lock className="h-4 w-4" />} type="password" {...form.register("password")} placeholder="Create a strong password" />
        </Field>
        <Button className="w-full" size="lg" disabled={register.isPending}>
          {register.isPending ? "Creating account..." : "Create account"}
        </Button>
      </form>
    </AuthLayout>
  );
}

export function ForgotPasswordPage() {
  const forgot = useForgotPassword();
  const form = useForm<z.infer<typeof forgotSchema>>({
    resolver: zodResolver(forgotSchema),
    defaultValues: { email: "" },
  });

  const onSubmit = form.handleSubmit(async (values: z.infer<typeof forgotSchema>) => {
    await forgot.mutateAsync(values);
  });

  return (
    <AuthLayout
      title="Reset your password"
      description="We'll initiate your reset flow and, in non-production environments, return the reset token."
      footer={
        <Link to="/login" className="text-sm font-semibold text-primary">
          Back to sign in
        </Link>
      }
    >
      <form className="space-y-4" onSubmit={onSubmit}>
        <Field label="Email" error={form.formState.errors.email?.message}>
          <TextInput icon={<Mail className="h-4 w-4" />} {...form.register("email")} placeholder="name@example.com" />
        </Field>
        <Button className="w-full" size="lg" disabled={forgot.isPending}>
          {forgot.isPending ? "Submitting..." : "Send reset instructions"}
        </Button>
        {forgot.data ? (
          <Card className="border-accent/40 bg-accent/10 p-4">
            <p className="text-sm font-medium text-foreground">{forgot.data.message}</p>
            {forgot.data.reset_token ? <p className="mt-2 break-all text-xs text-muted-foreground">Reset token: {forgot.data.reset_token}</p> : null}
          </Card>
        ) : null}
      </form>
    </AuthLayout>
  );
}

function AuthLayout({
  title,
  description,
  children,
  footer,
}: {
  title: string;
  description: string;
  children: ReactNode;
  footer?: ReactNode;
}) {
  return (
    <MarketingShell>
      <div className="grid min-h-[92vh] items-center gap-8 lg:grid-cols-[0.9fr_1.1fr]">
        <div className="hidden animate-fade-up lg:block">
          <Card className="overflow-hidden border-white/70 p-3 shadow-float">
            <div className="relative overflow-hidden rounded-[1.75rem]">
              <img
                src="/auth-food.jpg"
                alt="Silverbird BigMama restaurant spread"
                className="h-[720px] w-full object-cover"
              />
              <div className="absolute inset-0 bg-[linear-gradient(180deg,rgba(35,16,12,0.05),rgba(35,16,12,0.58))]" />
              <div className="absolute inset-x-0 bottom-0 p-8 text-white">
                <p className="text-xs font-semibold uppercase tracking-[0.35em] text-white/80">
                  Silverbird BigMama Restaurant
                </p>
                <h1 className="mt-4 max-w-xl text-4xl font-extrabold leading-tight">
                  Freshly prepared meals, beautifully presented and ready to order.
                </h1>
                <p className="mt-3 max-w-lg text-sm leading-6 text-white/82">
                  Sign in to explore the menu, place orders, and enjoy a smoother restaurant experience.
                </p>
              </div>
            </div>
          </Card>
        </div>
        <div className="animate-fade-up">
          <Card className="mx-auto max-w-xl p-6 sm:p-8">
            <div className="mb-8 space-y-2">
              <h2 className="text-3xl font-bold">{title}</h2>
              <p className="text-sm text-muted-foreground">{description}</p>
            </div>
            {children}
            {footer ? <div className="mt-6">{footer}</div> : null}
          </Card>
        </div>
      </div>
    </MarketingShell>
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
