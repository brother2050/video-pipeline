import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { stageApi } from "@/api";
import type { StageGenerateRequest, ReviewRequest, RollbackRequest } from "@/types";

export function useStages(projectId: string) {
  return useQuery({
    queryKey: ["stages", projectId],
    queryFn: () => stageApi.list(projectId),
    enabled: !!projectId,
  });
}

export function useStage(projectId: string, stageType: string) {
  return useQuery({
    queryKey: ["stage", projectId, stageType],
    queryFn: () => stageApi.get(projectId, stageType),
    enabled: !!projectId && !!stageType,
  });
}

export function useCandidates(projectId: string, stageType: string) {
  return useQuery({
    queryKey: ["candidates", projectId, stageType],
    queryFn: () => stageApi.listCandidates(projectId, stageType),
    enabled: !!projectId && !!stageType,
  });
}

export function useGenerate(projectId: string, stageType: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: StageGenerateRequest) => stageApi.generate(projectId, stageType, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["candidates", projectId, stageType] });
      qc.invalidateQueries({ queryKey: ["stage", projectId, stageType] });
      qc.invalidateQueries({ queryKey: ["stages", projectId] });
    },
  });
}

export function useSelectCandidate(projectId: string, stageType: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (candidateId: string) =>
      stageApi.selectCandidate(projectId, stageType, { candidate_id: candidateId }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["stage", projectId, stageType] });
    },
  });
}

export function useReview(projectId: string, stageType: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: ReviewRequest) => stageApi.review(projectId, stageType, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["stages", projectId] });
      qc.invalidateQueries({ queryKey: ["stage", projectId, stageType] });
      qc.invalidateQueries({ queryKey: ["project", projectId] });
    },
  });
}

export function useRollback(projectId: string, stageType: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: RollbackRequest) => stageApi.rollback(projectId, stageType, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["stages", projectId] });
      qc.invalidateQueries({ queryKey: ["project", projectId] });
    },
  });
}

export function useVersions(projectId: string, stageType: string) {
  return useQuery({
    queryKey: ["versions", projectId, stageType],
    queryFn: () => stageApi.listVersions(projectId, stageType),
    enabled: !!projectId && !!stageType,
  });
}

export function useUpdatePrompt(projectId: string, stageType: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (prompt: string) =>
      stageApi.updatePrompt(projectId, stageType, { prompt }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["stage", projectId, stageType] });
    },
  });
}
