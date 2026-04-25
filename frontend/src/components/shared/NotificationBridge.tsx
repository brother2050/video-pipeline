/**
 * Bridge: syncs UIStore notifications to shadcn/ui Toaster.
 * Place this component inside App.tsx to enable toast notifications.
 */

import { useEffect, useRef } from "react";
import { useUIStore } from "@/stores/uiStore";
import { useToast } from "@/hooks/use-toast";

export function NotificationBridge() {
  const notifications = useUIStore((s) => s.notifications);
  const { toast } = useToast();
  const lastCountRef = useRef(0);

  useEffect(() => {
    if (notifications.length > lastCountRef.current) {
      // New notification(s) added
      const newOnes = notifications.slice(lastCountRef.current);
      for (const n of newOnes) {
        const variant = n.type === "error" ? "destructive" as const : "default" as const;
        toast({
          title: n.type === "success" ? "成功" : n.type === "error" ? "错误" : n.type === "warning" ? "警告" : "通知",
          description: n.message,
          variant,
        });
      }
    }
    lastCountRef.current = notifications.length;
  }, [notifications, toast]);

  return null;
}
