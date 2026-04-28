import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { continuityApi } from "@/api";
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
} from "@/types/continuity";

export function useCharacterStates(projectId: string) {
  return useQuery({
    queryKey: ["character-states", projectId],
    queryFn: () => continuityApi.characterStates.list(projectId),
    enabled: !!projectId,
  });
}

export function useCharacterState(stateId: string) {
  return useQuery({
    queryKey: ["character-state", stateId],
    queryFn: () => continuityApi.characterStates.get(stateId),
    enabled: !!stateId,
  });
}

export function useCreateCharacterState() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: CharacterStateCreate) => continuityApi.characterStates.create(data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["character-states", variables.project_id] });
    },
  });
}

export function useUpdateCharacterState() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ stateId, data }: { stateId: string; data: CharacterStateUpdate }) =>
      continuityApi.characterStates.update(stateId, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["character-state", variables.stateId] });
    },
  });
}

export function useDeleteCharacterState() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (stateId: string) => continuityApi.characterStates.delete(stateId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["character-states"] });
    },
  });
}

export function useSceneAssets(projectId: string) {
  return useQuery({
    queryKey: ["scene-assets", projectId],
    queryFn: () => continuityApi.sceneAssets.list(projectId),
    enabled: !!projectId,
  });
}

export function useSceneAsset(assetId: string) {
  return useQuery({
    queryKey: ["scene-asset", assetId],
    queryFn: () => continuityApi.sceneAssets.get(assetId),
    enabled: !!assetId,
  });
}

export function useCreateSceneAsset() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: SceneAssetCreate) => continuityApi.sceneAssets.create(data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["scene-assets", variables.project_id] });
    },
  });
}

export function useUpdateSceneAsset() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ assetId, data }: { assetId: string; data: SceneAssetUpdate }) =>
      continuityApi.sceneAssets.update(assetId, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["scene-asset", variables.assetId] });
    },
  });
}

export function useDeleteSceneAsset() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (assetId: string) => continuityApi.sceneAssets.delete(assetId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["scene-assets"] });
    },
  });
}

export function usePacingTemplates() {
  return useQuery({
    queryKey: ["pacing-templates"],
    queryFn: () => continuityApi.pacingTemplates.list(),
  });
}

export function usePacingTemplate(templateId: string) {
  return useQuery({
    queryKey: ["pacing-template", templateId],
    queryFn: () => continuityApi.pacingTemplates.get(templateId),
    enabled: !!templateId,
  });
}

export function useCreatePacingTemplate() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: PacingTemplateCreate) => continuityApi.pacingTemplates.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["pacing-templates"] });
    },
  });
}

export function useUpdatePacingTemplate() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ templateId, data }: { templateId: string; data: Partial<PacingTemplateCreate> }) =>
      continuityApi.pacingTemplates.update(templateId, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["pacing-template", variables.templateId] });
      queryClient.invalidateQueries({ queryKey: ["pacing-templates"] });
    },
  });
}

export function useDeletePacingTemplate() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (templateId: string) => continuityApi.pacingTemplates.delete(templateId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["pacing-templates"] });
    },
  });
}

export function useValidatePacing() {
  return useMutation({
    mutationFn: (request: PacingValidationRequest) => continuityApi.pacingTemplates.validate(request),
  });
}

export function useComplianceReports(projectId: string) {
  return useQuery({
    queryKey: ["compliance-reports", projectId],
    queryFn: () => continuityApi.complianceReports.list(projectId),
    enabled: !!projectId,
  });
}

export function useComplianceReport(reportId: string) {
  return useQuery({
    queryKey: ["compliance-report", reportId],
    queryFn: () => continuityApi.complianceReports.get(reportId),
    enabled: !!reportId,
  });
}

export function useCheckCompliance() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (request: ComplianceCheckRequest) => continuityApi.complianceReports.check(request),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["compliance-reports", variables.project_id] });
    },
  });
}

export function useConsistencyChecks(projectId: string) {
  return useQuery({
    queryKey: ["consistency-checks", projectId],
    queryFn: () => continuityApi.consistencyChecks.list(projectId),
    enabled: !!projectId,
  });
}

export function useConsistencyCheck(checkId: string) {
  return useQuery({
    queryKey: ["consistency-check", checkId],
    queryFn: () => continuityApi.consistencyChecks.get(checkId),
    enabled: !!checkId,
  });
}

export function useCheckConsistency() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (request: ConsistencyCheckRequest) => continuityApi.consistencyChecks.check(request),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["consistency-checks", variables.project_id] });
    },
  });
}