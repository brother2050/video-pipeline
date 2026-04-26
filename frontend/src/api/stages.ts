import client from "./client";
import type {
  StageResponse,
  StageGenerateRequest,
  StagePromptUpdate,
  StageConfigUpdate,
  CandidateResponse,
  CandidateSelectRequest,
  ReviewRequest,
  RollbackRequest,
  RollbackResponse,
  VersionResponse,
} from "@/types";

export const stageApi = {
  list: async (projectId: string): Promise<StageResponse[]> => {
    const resp = await client.get(`/projects/${projectId}/stages`);
    return resp.data as StageResponse[];
  },

  get: async (projectId: string, stageType: string): Promise<StageResponse> => {
    const resp = await client.get(`/projects/${projectId}/stages/${stageType}`);
    return resp.data as StageResponse;
  },

  updatePrompt: async (projectId: string, stageType: string, data: StagePromptUpdate): Promise<StageResponse> => {
    const resp = await client.put(`/projects/${projectId}/stages/${stageType}/prompt`, data);
    return resp.data as StageResponse;
  },

  updateConfig: async (projectId: string, stageType: string, data: StageConfigUpdate): Promise<StageResponse> => {
    const resp = await client.put(`/projects/${projectId}/stages/${stageType}/config`, data);
    return resp.data as StageResponse;
  },

  generate: async (projectId: string, stageType: string, data: StageGenerateRequest): Promise<CandidateResponse[]> => {
    const resp = await client.post(`/projects/${projectId}/stages/${stageType}/generate`, data);
    return resp.data as CandidateResponse[];
  },

  listCandidates: async (projectId: string, stageType: string): Promise<CandidateResponse[]> => {
    const resp = await client.get(`/projects/${projectId}/stages/${stageType}/candidates`);
    return resp.data as CandidateResponse[];
  },

  getCandidateDetail: async (projectId: string, stageType: string, candidateId: string): Promise<CandidateResponse> => {
    const resp = await client.get(`/projects/${projectId}/stages/${stageType}/candidates/${candidateId}`);
    return resp.data as CandidateResponse;
  },

  selectCandidate: async (projectId: string, stageType: string, data: CandidateSelectRequest): Promise<StageResponse> => {
    const resp = await client.post(`/projects/${projectId}/stages/${stageType}/select`, data);
    return resp.data as StageResponse;
  },

  review: async (projectId: string, stageType: string, data: ReviewRequest): Promise<StageResponse> => {
    const resp = await client.post(`/projects/${projectId}/stages/${stageType}/review`, data);
    return resp.data as StageResponse;
  },

  rollback: async (projectId: string, stageType: string, data: RollbackRequest): Promise<RollbackResponse> => {
    const resp = await client.post(`/projects/${projectId}/stages/${stageType}/rollback`, data);
    return resp.data as RollbackResponse;
  },

  listVersions: async (projectId: string, stageType: string): Promise<VersionResponse[]> => {
    const resp = await client.get(`/projects/${projectId}/stages/${stageType}/versions`);
    return resp.data as VersionResponse[];
  },
};