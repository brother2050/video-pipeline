import { NavLink } from "react-router-dom";
import { LayoutDashboard, FolderOpen, Server, Settings2, Cog, ChevronLeft, ChevronRight } from "lucide-react";
import { useUIStore } from "@/stores/uiStore";
import { cn } from "@/lib/utils";

const navItems = [
  { to: "/dashboard", icon: LayoutDashboard, label: "仪表板" },
  { to: "/projects", icon: FolderOpen, label: "项目" },
  { to: "/nodes", icon: Server, label: "节点" },
  { to: "/suppliers", icon: Settings2, label: "供应商" },
  { to: "/settings", icon: Cog, label: "设置" },
];

export function Sidebar() {
  const collapsed = useUIStore((s) => s.sidebarCollapsed);
  const toggle = useUIStore((s) => s.toggleSidebar);

  return (
    <aside className={cn(
      "fixed left-0 top-0 h-full bg-card border-r flex flex-col transition-all duration-200 z-20",
      collapsed ? "w-16" : "w-60"
    )}>
      <div className="h-14 flex items-center px-4 border-b">
        {!collapsed && <span className="font-semibold text-lg">VideoPipeline</span>}
        {collapsed && <span className="font-semibold text-sm mx-auto">VP</span>}
      </div>
      <nav className="flex-1 py-2">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) => cn(
              "flex items-center gap-3 px-4 py-2.5 text-sm transition-colors",
              isActive ? "bg-accent text-accent-foreground font-medium" : "text-muted-foreground hover:text-foreground hover:bg-accent/50"
            )}
          >
            <item.icon className="h-4 w-4 shrink-0" />
            {!collapsed && <span>{item.label}</span>}
          </NavLink>
        ))}
      </nav>
      <button
        onClick={toggle}
        className="h-10 flex items-center justify-center border-t text-muted-foreground hover:text-foreground"
      >
        {collapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
      </button>
    </aside>
  );
}
