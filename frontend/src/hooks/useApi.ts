import { useQuery } from "@tanstack/react-query";
import { systemApi } from "@/api";

export function useSystemStatus() {
  return useQuery({
    queryKey: ["systemStatus"],
    queryFn: () => systemApi.status(),
    refetchInterval: 30_000,
  });
}

export function useHealthCheck() {
  return useQuery({
    queryKey: ["health"],
    queryFn: () => systemApi.health(),
    refetchInterval: 10_000,
  });
}
