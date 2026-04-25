import { useWebSocketStore } from "@/stores/websocketStore";
import { useUIStore } from "@/stores/uiStore";
import { Wifi, WifiOff, Sun, Moon } from "lucide-react";
import { cn } from "@/lib/utils";

export function Header() {
  const connected = useWebSocketStore((s) => s.connected);
  const theme = useUIStore((s) => s.theme);
  const setTheme = useUIStore((s) => s.setTheme);

  return (
    <header className="h-14 border-b flex items-center justify-between px-6 bg-card">
      <div />
      <div className="flex items-center gap-4">
        <div className={cn("flex items-center gap-1.5 text-xs", connected ? "text-green-600" : "text-red-500")}>
          {connected ? <Wifi className="h-3.5 w-3.5" /> : <WifiOff className="h-3.5 w-3.5" />}
          <span>{connected ? "已连接" : "断开"}</span>
        </div>
        <button
          onClick={() => setTheme(theme === "light" ? "dark" : "light")}
          className="text-muted-foreground hover:text-foreground"
        >
          {theme === "light" ? <Moon className="h-4 w-4" /> : <Sun className="h-4 w-4" />}
        </button>
      </div>
    </header>
  );
}
