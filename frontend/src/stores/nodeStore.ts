import { create } from "zustand";
import type { NodeResponse } from "@/types";

interface NodeState {
  nodes: NodeResponse[];
  setNodes: (nodes: NodeResponse[]) => void;
  updateNodeStatus: (nodeId: string, status: string) => void;
}

export const useNodeStore = create<NodeState>((set, get) => ({
  nodes: [],
  setNodes: (nodes) => set({ nodes }),
  updateNodeStatus: (nodeId, status) => {
    set({
      nodes: get().nodes.map((n) =>
        n.id === nodeId ? { ...n, status: status as NodeResponse["status"] } : n
      ),
    });
  },
}));
