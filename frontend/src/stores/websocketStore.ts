import { create } from "zustand";
import type { WSMessage } from "@/types";

interface WebSocketState {
  connected: boolean;
  lastMessage: WSMessage | null;
  subscriptions: Set<string>;
  connect: () => void;
  disconnect: () => void;
  subscribe: (projectId: string) => void;
  unsubscribe: (projectId: string) => void;
  send: (message: Record<string, unknown>) => void;
}

let ws: WebSocket | null = null;
let reconnectTimer: ReturnType<typeof setTimeout> | null = null;
let reconnectDelay = 1000;
let connecting = false;

const messageListeners: Set<(msg: WSMessage) => void> = new Set();

export function onWSMessage(listener: (msg: WSMessage) => void): () => void {
  messageListeners.add(listener);
  return () => {
    messageListeners.delete(listener);
  };
}

function getWsUrl(): string {
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  return `${protocol}//${window.location.host}/ws`;
}

export const useWebSocketStore = create<WebSocketState>((set, get) => ({
  connected: false,
  lastMessage: null,
  subscriptions: new Set<string>(),

  connect: () => {
    if (connecting) return;
    if (ws && (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING)) {
      return;
    }

    connecting = true;
    const socket = new WebSocket(getWsUrl());
    ws = socket;

    socket.onopen = () => {
      // 旧连接的回调，直接忽略
      if (ws !== socket) return;

      connecting = false;
      set({ connected: true });
      reconnectDelay = 1000;
      const subs = get().subscriptions;
      subs.forEach((projectId) => {
        socket.send(JSON.stringify({ type: "subscribe", data: { project_id: projectId } }));
      });
    };

    socket.onmessage = (event) => {
      if (ws !== socket) return;

      try {
        const msg = JSON.parse(event.data as string) as WSMessage;
        if (msg.type === "ping") {
          socket.send(JSON.stringify({ type: "pong", data: {}, timestamp: new Date().toISOString() }));
          return;
        }
        set({ lastMessage: msg });
        messageListeners.forEach((listener) => listener(msg));
      } catch {
        // ignore parse errors
      }
    };

    socket.onclose = () => {
      // 旧连接关闭，不触发重连
      if (ws !== socket) return;

      connecting = false;
      set({ connected: false });
      ws = null;
      reconnectTimer = setTimeout(() => {
        reconnectDelay = Math.min(reconnectDelay * 2, 30_000);
        get().connect();
      }, reconnectDelay);
    };

    socket.onerror = () => {
      socket.close();
    };
  },

  disconnect: () => {
    connecting = false;
    if (reconnectTimer) {
      clearTimeout(reconnectTimer);
      reconnectTimer = null;
    }
    if (ws) {
      const stale = ws;
      ws = null;          // 先置空，让 onclose 看到 ws !== socket
      stale.close();       // 再关闭
    }
    set({ connected: false });
  },

  subscribe: (projectId: string) => {
    const subs = new Set(get().subscriptions);
    subs.add(projectId);
    set({ subscriptions: subs });
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: "subscribe", data: { project_id: projectId } }));
    }
  },

  unsubscribe: (projectId: string) => {
    const subs = new Set(get().subscriptions);
    subs.delete(projectId);
    set({ subscriptions: subs });
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: "unsubscribe", data: { project_id: projectId } }));
    }
  },

  send: (message: Record<string, unknown>) => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(message));
    }
  },
}));
