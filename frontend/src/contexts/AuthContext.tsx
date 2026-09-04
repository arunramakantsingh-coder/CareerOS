"use client";

import React, { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { useRouter } from "next/navigation";
import { resolveApiBaseUrl } from "@/lib/api/client";

interface User { id: string; email: string; name: string; is_active: boolean; }
interface AuthContextType { user: User | null; token: string | null; isLoading: boolean; login: (email: string, password: string) => Promise<void>; register: (email: string, password: string, name: string, tenant_name?: string) => Promise<void>; logout: () => void; isAuthenticated: boolean; }

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const storedToken = localStorage.getItem("access_token") || localStorage.getItem("careeros_token");
    const storedUser = localStorage.getItem("user");
    if (storedToken) setToken(storedToken);
    if (storedUser) { try { setUser(JSON.parse(storedUser)); } catch { localStorage.removeItem("user"); } }
    setIsLoading(false);
  }, []);

  const login = async (email: string, password: string) => {
    const api = resolveApiBaseUrl();
    const response = await fetch(`${api}/api/v1/auth/login`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ email, password }) });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(typeof data.detail === "string" ? data.detail : "Login failed");
    const accessToken = data.access_token;
    if (!accessToken) throw new Error("Login succeeded but no access token was returned.");
    const userResponse = await fetch(`${api}/api/v1/auth/me`, { headers: { "Authorization": `Bearer ${accessToken}` }, cache: "no-store" });
    const userData = await userResponse.json().catch(() => ({}));
    if (!userResponse.ok) throw new Error(typeof userData.detail === "string" ? userData.detail : "Failed to fetch user info");
    localStorage.setItem("access_token", accessToken);
    localStorage.setItem("user", JSON.stringify(userData));
    setToken(accessToken); setUser(userData); router.push("/");
  };

  const register = async (email: string, password: string, name: string, tenant_name?: string) => {
    const api = resolveApiBaseUrl();
    const response = await fetch(`${api}/api/v1/auth/register`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ email, password, name, tenant_name: tenant_name || "default" }) });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(typeof data.detail === "string" ? data.detail : "Registration failed");
    await login(email, password);
  };

  const logout = () => { localStorage.removeItem("access_token"); localStorage.removeItem("careeros_token"); localStorage.removeItem("user"); setToken(null); setUser(null); router.push("/login"); };
  return <AuthContext.Provider value={{ user, token, isLoading, login, register, logout, isAuthenticated: !!token && !!user }}>{children}</AuthContext.Provider>;
}

export function useAuth() { const context = useContext(AuthContext); if (context === undefined) throw new Error("useAuth must be used within AuthProvider"); return context; }
