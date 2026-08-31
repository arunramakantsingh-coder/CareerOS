"use client";

import React, { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { useRouter } from "next/navigation";

interface User { id: string; email: string; name: string; is_active: boolean; }
interface AuthContextType { user: User | null; token: string | null; isLoading: boolean; login: (email: string, password: string) => Promise<void>; register: (email: string, password: string, name: string, tenant_name?: string) => Promise<void>; logout: () => void; isAuthenticated: boolean; }

const AuthContext = createContext<AuthContextType | undefined>(undefined);
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null); const [token, setToken] = useState<string | null>(null); const [isLoading, setIsLoading] = useState(true); const router = useRouter();
  useEffect(() => { const storedToken = localStorage.getItem("access_token"); const storedUser = localStorage.getItem("user"); if (storedToken && storedUser) { setToken(storedToken); try { setUser(JSON.parse(storedUser)); } catch { localStorage.removeItem("user"); } } setIsLoading(false); }, []);

  const login = async (email: string, password: string) => {
    const response = await fetch(`${API_URL}/api/v1/auth/login`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ email, password }) });
    if (!response.ok) { const error = await response.json(); throw new Error(error.detail || "Login failed"); }
    const data = await response.json(); const accessToken = data.access_token;
    const userResponse = await fetch(`${API_URL}/api/v1/auth/me`, { headers: { "Authorization": `Bearer ${accessToken}` } });
    if (!userResponse.ok) throw new Error("Failed to fetch user info");
    const userData = await userResponse.json(); localStorage.setItem("access_token", accessToken); localStorage.setItem("user", JSON.stringify(userData)); setToken(accessToken); setUser(userData);
    router.push("/");
  };

  const register = async (email: string, password: string, name: string, tenant_name?: string) => {
    const response = await fetch(`${API_URL}/api/v1/auth/register`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ email, password, name, tenant_name: tenant_name || "default" }) });
    if (!response.ok) { const error = await response.json(); throw new Error(error.detail || "Registration failed"); }
    await login(email, password);
  };

  const logout = () => { localStorage.removeItem("access_token"); localStorage.removeItem("user"); setToken(null); setUser(null); router.push("/login"); };
  return <AuthContext.Provider value={{ user, token, isLoading, login, register, logout, isAuthenticated: !!token && !!user }}>{children}</AuthContext.Provider>;
}

export function useAuth() { const context = useContext(AuthContext); if (context === undefined) throw new Error("useAuth must be used within an AuthProvider"); return context; }
