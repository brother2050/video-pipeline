import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { supplierApi } from "@/api";
import type { CapabilityConfigUpdate, SupplierTestRequest } from "@/types";

export function useSuppliers() {
  return useQuery({
    queryKey: ["suppliers"],
    queryFn: () => supplierApi.list(),
  });
}

export function useSupplierConfig(capability: string) {
  return useQuery({
    queryKey: ["supplier", capability],
    queryFn: () => supplierApi.get(capability),
    enabled: !!capability,
  });
}

export function useUpdateSupplier(capability: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: CapabilityConfigUpdate) => supplierApi.update(capability, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["suppliers"] });
      qc.invalidateQueries({ queryKey: ["supplier", capability] });
    },
  });
}

export function useTestSupplier() {
  return useMutation({
    mutationFn: (data: SupplierTestRequest) => supplierApi.test(data),
  });
}

export function useAnalyzeWorkflow() {
  return useMutation({
    mutationFn: (workflow: Record<string, unknown>) => supplierApi.analyzeWorkflow(workflow),
  });
}

export function useUploadWorkflow() {
  return useMutation({
    mutationFn: (file: File) => supplierApi.uploadWorkflow(file),
  });
}
