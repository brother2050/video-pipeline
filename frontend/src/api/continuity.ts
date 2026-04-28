import client from "./client";
import type {
  CharacterState,
  CharacterStateCreate,
  CharacterStateUpdate,
  SceneAsset,
  SceneAssetCreate,
  SceneAssetUpdate,
  PacingTemplate,
  PacingTemplateCreate,
  PacingValidationRequest,
  PacingValidationResult,
  ComplianceReport,
  ComplianceCheckRequest,
  ConsistencyCheck,
  ConsistencyCheckRequest,
  AsyncTaskResponse,
} from "@/types/continuity";

export const continuityApi = {
  characterStates: {
    list: async (projectId: string): Promise<CharacterState[]> => {
      const resp = await client.get(`/continuity/characters/states`, {
        params: { project_id: projectId },
      });
      return resp.data as CharacterState[];
    },

    get: async (stateId: string): Promise<CharacterState> => {
      const resp = await client.get(`/continuity/characters/states/${stateId}`);
      return resp.data as CharacterState;
    },

    create: async (data: CharacterStateCreate): Promise<CharacterState> => {
      const resp = await client.post("/continuity/characters/states", data);
      return resp.data as CharacterState;
    },

    update: async (stateId: string, data: CharacterStateUpdate): Promise<CharacterState> => {
      const resp = await client.put(`/continuity/characters/states/${stateId}`, data);
      return resp.data as CharacterState;
    },

    delete: async (stateId: string): Promise<void> => {
      await client.delete(`/continuity/characters/states/${stateId}`);
    },
  },

  sceneAssets: {
    list: async (projectId: string): Promise<SceneAsset[]> => {
      const resp = await client.get(`/continuity/scenes/assets`, {
        params: { project_id: projectId },
      });
      return resp.data as SceneAsset[];
    },

    get: async (assetId: string): Promise<SceneAsset> => {
      const resp = await client.get(`/continuity/scenes/assets/${assetId}`);
      return resp.data as SceneAsset;
    },

    create: async (data: SceneAssetCreate): Promise<SceneAsset> => {
      const resp = await client.post("/continuity/scenes/assets", data);
      return resp.data as SceneAsset;
    },

    update: async (assetId: string, data: SceneAssetUpdate): Promise<SceneAsset> => {
      const resp = await client.put(`/continuity/scenes/assets/${assetId}`, data);
      return resp.data as SceneAsset;
    },

    delete: async (assetId: string): Promise<void> => {
      await client.delete(`/continuity/scenes/assets/${assetId}`);
    },
  },

  pacingTemplates: {
    list: async (): Promise<PacingTemplate[]> => {
      const resp = await client.get("/pacing/templates");
      return resp.data as PacingTemplate[];
    },

    get: async (templateId: string): Promise<PacingTemplate> => {
      const resp = await client.get(`/pacing/templates/${templateId}`);
      return resp.data as PacingTemplate;
    },

    create: async (data: PacingTemplateCreate): Promise<PacingTemplate> => {
      const resp = await client.post("/pacing/templates", data);
      return resp.data as PacingTemplate;
    },

    update: async (templateId: string, data: Partial<PacingTemplateCreate>): Promise<PacingTemplate> => {
      const resp = await client.put(`/pacing/templates/${templateId}`, data);
      return resp.data as PacingTemplate;
    },

    delete: async (templateId: string): Promise<void> => {
      await client.delete(`/pacing/templates/${templateId}`);
    },

    validate: async (request: PacingValidationRequest): Promise<PacingValidationResult> => {
      const resp = await client.post("/pacing/validate", request);
      return resp.data as PacingValidationResult;
    },
  },

  complianceReports: {
    list: async (projectId: string): Promise<ComplianceReport[]> => {
      const resp = await client.get(`/compliance/reports`, {
        params: { project_id: projectId },
      });
      return resp.data as ComplianceReport[];
    },

    get: async (reportId: string): Promise<ComplianceReport> => {
      const resp = await client.get(`/compliance/reports/${reportId}`);
      return resp.data as ComplianceReport;
    },

    check: async (request: ComplianceCheckRequest): Promise<AsyncTaskResponse> => {
      const resp = await client.post("/compliance/check", request);
      return resp.data as AsyncTaskResponse;
    },

    getTaskStatus: async (taskId: string): Promise<any> => {
      const resp = await client.get(`/compliance/tasks/${taskId}`);
      return resp.data;
    },
  },

  consistencyChecks: {
    list: async (projectId: string): Promise<ConsistencyCheck[]> => {
      const resp = await client.get(`/continuity/consistency/checks`, {
        params: { project_id: projectId },
      });
      return resp.data as ConsistencyCheck[];
    },

    get: async (checkId: string): Promise<ConsistencyCheck> => {
      const resp = await client.get(`/continuity/consistency/checks/${checkId}`);
      return resp.data as ConsistencyCheck;
    },

    check: async (request: ConsistencyCheckRequest): Promise<ConsistencyCheck> => {
      const resp = await client.post("/continuity/consistency/check", request);
      return resp.data as ConsistencyCheck;
    },
  },
};