import client from "./client";
import type { SystemStatus } from "@/types";

export const systemApi = {
  health: async (): Promise<{ status: string }> => {
    const resp = await client.get("/system/health");
    return resp.data as { status: string };
  },

  status: async (): Promise<SystemStatus> => {
    const resp = await client.get("/system/status");
    return resp.data as SystemStatus;
  },
};
