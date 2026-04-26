import apiClient from "./client";

export interface ConstantsResponse {
  genres: string[];
  providers: Record<string, string[]>;
  capability_labels: Record<string, string>;
  resolutions: string[];
  subtitle_positions: string[];
  audio_codecs: string[];
  video_bitrates: string[];
  audio_bitrates: string[];
  fonts: string[];
  subtitle_colors: string[];
}

export const constantsApi = {
  getAll: () => apiClient.get<ConstantsResponse>("/constants/all").then(res => res.data),
  getGenres: () => apiClient.get<string[]>("/constants/genres").then(res => res.data),
  getProviders: (capability: string) => apiClient.get<string[]>(`/constants/providers/${capability}`).then(res => res.data),
  getResolutions: () => apiClient.get<string[]>("/constants/resolutions").then(res => res.data),
  getSubtitlePositions: () => apiClient.get<string[]>("/constants/subtitle-positions").then(res => res.data),
  getAudioCodecs: () => apiClient.get<string[]>("/constants/audio-codecs").then(res => res.data),
  getVideoBitrates: () => apiClient.get<string[]>("/constants/video-bitrates").then(res => res.data),
  getAudioBitrates: () => apiClient.get<string[]>("/constants/audio-bitrates").then(res => res.data),
  getFonts: () => apiClient.get<string[]>("/constants/fonts").then(res => res.data),
  getSubtitleColors: () => apiClient.get<string[]>("/constants/subtitle-colors").then(res => res.data),
  getCapabilityLabels: () => apiClient.get<Record<string, string>>("/constants/capability-labels").then(res => res.data),
};