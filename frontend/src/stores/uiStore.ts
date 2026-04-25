import { create } from "zustand";

interface Notification {
  id: string;
  type: "info" | "success" | "warning" | "error";
  message: string;
  timestamp: number;
}

interface UIState {
  sidebarCollapsed: boolean;
  theme: "light" | "dark";
  notifications: Notification[];
  toggleSidebar: () => void;
  setTheme: (theme: "light" | "dark") => void;
  addNotification: (type: Notification["type"], message: string) => void;
  removeNotification: (id: string) => void;
}

export const useUIStore = create<UIState>((set, get) => ({
  sidebarCollapsed: false,
  theme: (localStorage.getItem("vp-theme") as "light" | "dark") || "light",
  notifications: [],

  toggleSidebar: () => {
    set({ sidebarCollapsed: !get().sidebarCollapsed });
  },

  setTheme: (theme) => {
    localStorage.setItem("vp-theme", theme);
    document.documentElement.classList.toggle("dark", theme === "dark");
    set({ theme });
  },

  addNotification: (type, message) => {
    const id = crypto.randomUUID();
    const notification: Notification = { id, type, message, timestamp: Date.now() };
    set({ notifications: [...get().notifications, notification] });
    setTimeout(() => {
      get().removeNotification(id);
    }, 5000);
  },

  removeNotification: (id) => {
    set({ notifications: get().notifications.filter((n) => n.id !== id) });
  },
}));
