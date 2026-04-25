import { useEffect } from "react";
import { useWebSocketStore, onWSMessage } from "@/stores/websocketStore";
import { useNodeStore } from "@/stores/nodeStore";
import { useUIStore } from "@/stores/uiStore";

export function useWebSocket() {
  const connect = useWebSocketStore((s) => s.connect);
  const disconnect = useWebSocketStore((s) => s.disconnect);

  useEffect(() => {
    // 延迟 300ms，等 Vite 代理和后端都就绪
    const timer = setTimeout(() => {
      connect();
    }, 300);
    return () => {
      clearTimeout(timer);
      disconnect();
    };
  }, [connect, disconnect]);

  // 监听节点状态变更
  useEffect(() => {
    return onWSMessage((msg) => {
      if (msg.type === "node_status") {
        const data = msg.data as { node_id: string; new_status: string };
        useNodeStore.getState().updateNodeStatus(data.node_id, data.new_status);
      }
      if (msg.type === "stage_update") {
        const data = msg.data as { stage_type: string; status: string };
        useUIStore.getState().addNotification("info", `阶段 ${data.stage_type} 状态更新: ${data.status}`);
      }
    });
  }, []);
}
