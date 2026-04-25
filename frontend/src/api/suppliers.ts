import client from "./client";
import type {
  CapabilityConfigResponse,
  CapabilityConfigUpdate,
  SupplierTestRequest,
  SupplierTestResponse,
  WorkflowAnalysis,
} from "@/types";

export const supplierApi = {
  list: async (): Promise<CapabilityConfigResponse[]> => {
    const resp = await client.get("/suppliers");
    return resp.data as CapabilityConfigResponse[];
  },

  get: async (capability: string): Promise<CapabilityConfigResponse> => {
    const resp = await client.get(`/suppliers/${capability}`);
    return resp.data as CapabilityConfigResponse;
  },

  update: async (capability: string, data: CapabilityConfigUpdate): Promise<CapabilityConfigResponse> => {
    const resp = await client.put(`/suppliers/${capability}`, data);
    return resp.data as CapabilityConfigResponse;
  },

  test: async (data: SupplierTestRequest): Promise<SupplierTestResponse> => {
    const resp = await client.post("/suppliers/test", data);
    return resp.data as SupplierTestResponse;
  },

  analyzeWorkflow: async (workflow: Record<string, unknown>): Promise<WorkflowAnalysis> => {
    const resp = await client.post("/suppliers/analyze-workflow", { workflow });
    return resp.data as WorkflowAnalysis;
  },

  uploadWorkflow: async (file: File): Promise<{ path: string }> => {
    const formData = new FormData();
    formData.append("file", file);
    const resp = await client.post("/suppliers/upload-workflow", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return resp.data as { path: string };
  },
};
