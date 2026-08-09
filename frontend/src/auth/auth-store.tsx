import { createContext, useContext, useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";
import { clearSession, readSession, type SessionRole, type SessionState } from "@/lib/session";

interface AuthContextValue {
  session: SessionState | null;
  role: SessionRole | null;
  isAuthenticated: boolean;
  setSession: (session: SessionState | null) => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [session, setSessionState] = useState<SessionState | null>(() => readSession());

  const value = useMemo<AuthContextValue>(
    () => ({
      session,
      role: session?.role ?? null,
      isAuthenticated: Boolean(session?.accessToken),
      setSession: (nextSession) => {
        if (!nextSession) {
          clearSession();
        }
        setSessionState(nextSession);
      },
    }),
    [session],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}
