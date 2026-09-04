"use client";

import React, { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { useRouter } from "next/navigation";
import { resolveApiBaseUrl } from "@/lib/api/client";

interface User { id: string; email: string; name: string; is_active: boolean; }
interface AuthContextType {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, name: string, tenant_name?: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

async function fetchCurrentUser(api: string, accessToken: string): Promise<User> {
  const response = await fetch(`${api}/api/v1/auth/me`, {
    headers: { "Authorization": `Bearer ${accessToken}` },
    cache: "no-store",
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok || !data?.id) {
    const detail = typeof data?.detail === "string" ? data.detail : `Session validation failed (HTTP ${response.status}).`;
    throw new Error(detail);
  }
  return data as User;
}

function clearStoredSession() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("careeros_token");
  localStorage.removeItem("user");
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    let active = true;
    const api = resolveApiBaseUrl();
    const storedToken = localStorage.getItem("access_token") || localStorage.getItem("careeros_token");

    if (!storedToken) {
      setIsLoading(false);
      return;
    }

    (async () => {
      try {
        const currentUser = await fetchCurrentUser(api, storedToken);
        if (!active) return;
        localStorage.setItem("access_token", storedToken);
        localStorage.removeItem("careeros_token");
        localStorage.setItem("user", JSON.stringify(currentUser));
        setToken(storedToken);
        setUser(currentUser);
      } catch {
        if (!active) return;
        clearStoredSession();
        setToken(null);
        setUser(null);
      } finally {
        if (active) setIsLoading(false);
      }
    })();

    return () => { active = false; };
  }, []);

  const login = async (email: string, password: string) => {
    const api = resolveApiBaseUrl();
    const response = await fetch(`${api}/api/v1/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: email.trim(), password }),
      cache: "no-store",
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw new Error(typeof data.detail === "string" ? data.detail : `Login failed (HTTP ${response.status}).`);
    }

    const accessToken = data.access_token;
    if (!accessToken) throw new Error("Login succeeded but no access token was returned.");

    // Store the token before the session lookup so the application has one canonical
    // session location. If validation fails, the catch below removes it again.
    localStorage.setItem("access_token", accessToken);
    localStorage.removeItem("careeros_token");

    try {
      const currentUser = await fetchCurrentUser(api, accessToken);
      localStorage.setItem("user", JSON.stringify(currentUser));
      setToken(accessToken);
      setUser(currentUser);
      router.replace("/");
    } catch (error) {
      clearStoredSession();
      setToken(null);
      setUser(null);
      throw error;
    }
  };

  const register = async (email: string, password: string, name: string, tenant_name?: string) => {
    const api = resolveApiBaseUrl();
    const response = await fetch(`${api}/api/v1/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: email.trim(), password, name, tenant_name: tenant_name || "default" }),
      cache: "no-store",
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(typeof data.detail === "string" ? data.detail : `Registration failed (HTTP ${response.status}).`);
    await login(email, password);
  };

  const logout = () => {
    clearStoredSession();
    setToken(null);
    setUser(null);
    router.replace("/login");
  };

  return <AuthContext.Provider value={{ user, token, isLoading, login, register, logout, isAuthenticated: !!token && !!user }}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) throw new Error("useAuth must be used within AuthProvider");
  return context;
}
