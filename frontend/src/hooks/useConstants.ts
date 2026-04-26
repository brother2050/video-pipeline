import { useQuery } from "@tanstack/react-query";
import { constantsApi } from "@/api";

export function useConstants() {
  return useQuery({
    queryKey: ["constants"],
    queryFn: () => constantsApi.getAll(),
    staleTime: Infinity, // 常量不会频繁变化
  });
}

export function useGenres() {
  return useQuery({
    queryKey: ["constants", "genres"],
    queryFn: () => constantsApi.getGenres(),
    staleTime: Infinity,
  });
}

export function useProviders(capability: string) {
  return useQuery({
    queryKey: ["constants", "providers", capability],
    queryFn: () => constantsApi.getProviders(capability),
    staleTime: Infinity,
  });
}

export function useResolutions() {
  return useQuery({
    queryKey: ["constants", "resolutions"],
    queryFn: () => constantsApi.getResolutions(),
    staleTime: Infinity,
  });
}

export function useSubtitlePositions() {
  return useQuery({
    queryKey: ["constants", "subtitle-positions"],
    queryFn: () => constantsApi.getSubtitlePositions(),
    staleTime: Infinity,
  });
}

export function useAudioCodecs() {
  return useQuery({
    queryKey: ["constants", "audio-codecs"],
    queryFn: () => constantsApi.getAudioCodecs(),
    staleTime: Infinity,
  });
}

export function useVideoBitrates() {
  return useQuery({
    queryKey: ["constants", "video-bitrates"],
    queryFn: () => constantsApi.getVideoBitrates(),
    staleTime: Infinity,
  });
}

export function useAudioBitrates() {
  return useQuery({
    queryKey: ["constants", "audio-bitrates"],
    queryFn: () => constantsApi.getAudioBitrates(),
    staleTime: Infinity,
  });
}

export function useFonts() {
  return useQuery({
    queryKey: ["constants", "fonts"],
    queryFn: () => constantsApi.getFonts(),
    staleTime: Infinity,
  });
}

export function useSubtitleColors() {
  return useQuery({
    queryKey: ["constants", "subtitle-colors"],
    queryFn: () => constantsApi.getSubtitleColors(),
    staleTime: Infinity,
  });
}

export function useCapabilityLabels() {
  return useQuery({
    queryKey: ["constants", "capability-labels"],
    queryFn: () => constantsApi.getCapabilityLabels(),
    staleTime: Infinity,
  });
}