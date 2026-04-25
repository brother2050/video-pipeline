import client from "./client";
import type {
  ProjectCreate,
  ProjectUpdate,
  ProjectResponse,
  ProjectDetail,
  PaginatedData,
} from "@/types";

export const projectApi = {
  create: async (data: ProjectCreate): Promise<ProjectResponse> => {
    const resp = await client.post("/projects", data);
    return resp.data as ProjectResponse;
  },

  list: async (page: number, pageSize: number): Promise<PaginatedData<ProjectResponse>> => {
    const resp = await client.get("/projects", { params: { page, page_size: pageSize } });
    return resp.data as PaginatedData<ProjectResponse>;
  },

  get: async (id: string): Promise<ProjectDetail> => {
    const resp = await client.get(`/projects/${id}`);
    return resp.data as ProjectDetail;
  },

  update: async (id: string, data: ProjectUpdate): Promise<ProjectResponse> => {
    const resp = await client.put(`/projects/${id}`, data);
    return resp.data as ProjectResponse;
  },

  delete: async (id: string): Promise<void> => {
    await client.delete(`/projects/${id}`);
  },
};
