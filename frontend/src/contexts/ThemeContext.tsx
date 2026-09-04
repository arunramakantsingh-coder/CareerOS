"use client";

import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from "react";

export type CareerOSTheme = "light" | "dark" | "techno";
type ThemeContextValue = { theme: CareerOSTheme; setTheme: (theme: CareerOSTheme) => void };

const ThemeContext = createContext<ThemeContextValue | undefined>(undefined);
const STORAGE_KEY = "careeros-theme";

function applyTheme(theme: CareerOSTheme) {
  const root = document.documentElement;
  root.classList.toggle("dark", theme === "dark" || theme === "techno");
  root.dataset.theme = theme;
}

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setThemeState] = useState<CareerOSTheme>("light");
  useEffect(() => {
    const stored = localStorage.getItem(STORAGE_KEY) as CareerOSTheme | null;
    const next: CareerOSTheme = stored === "dark" || stored === "techno" ? stored : "light";
    setThemeState(next); applyTheme(next);
  }, []);
  const setTheme = (next: CareerOSTheme) => { setThemeState(next); localStorage.setItem(STORAGE_KEY, next); applyTheme(next); };
  const value = useMemo(() => ({ theme, setTheme }), [theme]);
  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) throw new Error("useTheme must be used within ThemeProvider");
  return context;
}
