import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { nodeApi } from "@/api";
import type { NodeCreate, NodeUpdate } from "@/types";

export function useNodes() {
  return useQuery({
    queryKey: ["nodes"],
    queryFn: () => nodeApi.list(),
  });
}

export function useCreateNode() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: NodeCreate) => nodeApi.create(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["nodes"] }),
  });
}

export function useUpdateNode(id: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: NodeUpdate) => nodeApi.update(id, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["nodes"] }),
  });
}

export function useDeleteNode() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => nodeApi.delete(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["nodes"] }),
  });
}

export function useToggleNode(id: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (enabled: boolean) => nodeApi.toggle(id, { enabled }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["nodes"] }),
  });
}

export function useNodeHealth(id: string) {
  return useQuery({
    queryKey: ["nodeHealth", id],
    queryFn: () => nodeApi.health(id),
    enabled: false,
  });
}
