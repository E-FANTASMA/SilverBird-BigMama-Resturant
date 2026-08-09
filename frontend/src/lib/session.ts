import { decodeJwtPayload } from "@/lib/utils";

export type SessionRole = "CUSTOMER" | "ADMIN" | "DELIVERY_PERSONNEL";

export interface SessionState {
  accessToken: string;
  refreshToken: string;
  tokenType: string;
  role: SessionRole;
}

const STORAGE_KEY = "silverbird.session";

export function deriveRoleFromToken(token: string): SessionRole {
  const payload = decodeJwtPayload(token);
  const role = payload?.role;
  if (role === "ADMIN" || role === "DELIVERY_PERSONNEL" || role === "CUSTOMER") {
    return role;
  }
  return "CUSTOMER";
}

export function saveSession(session: Omit<SessionState, "role"> & { role?: SessionRole }) {
  const nextSession: SessionState = {
    ...session,
    role: session.role ?? deriveRoleFromToken(session.accessToken),
  };
  localStorage.setItem(STORAGE_KEY, JSON.stringify(nextSession));
  return nextSession;
}

export function readSession() {
  const raw = localStorage.getItem(STORAGE_KEY);
  if (!raw) {
    return null;
  }
  try {
    return JSON.parse(raw) as SessionState;
  } catch {
    localStorage.removeItem(STORAGE_KEY);
    return null;
  }
}

export function clearSession() {
  localStorage.removeItem(STORAGE_KEY);
}
