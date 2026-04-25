import client from "./client";
import type {
  NodeCreate,
  NodeUpdate,
  NodeResponse,
  NodeToggleRequest,
  NodeHealthResponse,
} from "@/types";

export const nodeApi = {
  create: async (data: NodeCreate): Promise<NodeResponse> => {
    const resp = await client.post("/nodes", data);
    return resp.data as NodeResponse;
  },

  list: async (): Promise<NodeResponse[]> => {
    const resp = await client.get("/nodes");
    return resp.data as NodeResponse[];
  },

  get: async (id: string): Promise<NodeResponse> => {
    const resp = await client.get(`/nodes/${id}`);
    return resp.data as NodeResponse;
  },

  update: async (id: string, data: NodeUpdate): Promise<NodeResponse> => {
    const resp = await client.put(`/nodes/${id}`, data);
    return resp.data as NodeResponse;
  },

  delete: async (id: string): Promise<void> => {
    await client.delete(`/nodes/${id}`);
  },

  toggle: async (id: string, data: NodeToggleRequest): Promise<NodeResponse> => {
    const resp = await client.post(`/nodes/${id}/toggle`, data);
    return resp.data as NodeResponse;
  },

  health: async (id: string): Promise<NodeHealthResponse> => {
    const resp = await client.get(`/nodes/${id}/health`);
    return resp.data as NodeHealthResponse;
  },
};
