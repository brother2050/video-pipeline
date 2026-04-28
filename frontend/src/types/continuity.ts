import type { PaginatedData } from "./api";

export interface CharacterState {
  id: string;
  project_id: string;
  character_name: string;
  episode_start: number;
  episode_end: number | null;
  outfit_description: string;
  hairstyle: string;
  accessories: Record<string, any>;
  makeup: string;
  age_appearance: string;
  lora_path: string | null;
  embedding_path: string | null;
  reference_image_path: string | null;
  signature_items: Record<string, any>;
  notes: string;
  created_at: string;
  updated_at: string;
}

export interface CharacterStateCreate {
  project_id: string;
  character_name: string;
  episode_start: number;
  episode_end?: number | null;
  outfit_description?: string;
  hairstyle?: string;
  accessories?: Record<string, any>;
  makeup?: string;
  age_appearance?: string;
  lora_path?: string | null;
  embedding_path?: string | null;
  reference_image_path?: string | null;
  signature_items?: Record<string, any>;
  notes?: string;
}

export interface CharacterStateUpdate {
  episode_end?: number | null;
  outfit_description?: string;
  hairstyle?: string;
  accessories?: Record<string, any>;
  makeup?: string;
  age_appearance?: string;
  lora_path?: string | null;
  embedding_path?: string | null;
  reference_image_path?: string | null;
  signature_items?: Record<string, any>;
  notes?: string;
}

export interface SceneAsset {
  id: string;
  project_id: string;
  scene_name: string;
  scene_type: "interior" | "exterior" | "mixed";
  description: string;
  layout_description: string;
  lora_path: string | null;
  controlnet_depth_path: string | null;
  controlnet_edge_path: string | null;
  variants: Record<string, any>;
  reference_image_path: string | null;
  created_at: string;
  updated_at: string;
}

export interface SceneAssetCreate {
  project_id: string;
  scene_name: string;
  scene_type?: "interior" | "exterior" | "mixed";
  description?: string;
  layout_description?: string;
  lora_path?: string | null;
  controlnet_depth_path?: string | null;
  controlnet_edge_path?: string | null;
  variants?: Record<string, any>;
  reference_image_path?: string | null;
}

export interface SceneAssetUpdate {
  scene_name?: string;
  scene_type?: "interior" | "exterior" | "mixed";
  description?: string;
  layout_description?: string;
  lora_path?: string | null;
  controlnet_depth_path?: string | null;
  controlnet_edge_path?: string | null;
  variants?: Record<string, any>;
  reference_image_path?: string | null;
}

export interface PacingTemplate {
  id: string;
  name: string;
  description: string;
  genre: string;
  structure: Record<string, any>;
  hook_3sec_config: Record<string, any>;
  cliffhanger_config: Record<string, any>;
  target_duration_sec: number;
  usage_count: number;
  avg_completion_rate: number;
  created_at: string;
  updated_at: string;
}

export interface PacingTemplateCreate {
  name: string;
  description?: string;
  genre?: string;
  structure?: Record<string, any>;
  hook_3sec_config?: Record<string, any>;
  cliffhanger_config?: Record<string, any>;
  target_duration_sec?: number;
}

export interface PacingValidationRequest {
  scene_content: Record<string, any>;
  template_id?: string;
  hook_config?: Record<string, any>;
}

export interface PacingValidationResult {
  valid: boolean;
  issues: Array<{
    type: string;
    message: string;
    severity: "error" | "warning" | "info";
  }>;
}

export interface ComplianceReport {
  id: string;
  project_id: string;
  check_type: "face_recognition" | "music_copyright" | "content_moderation";
  episode_number: number | null;
  stage_type: string | null;
  status: "pending" | "completed" | "failed";
  violations: number;
  violations_detail: Record<string, any>;
  checked_at: string;
}

export interface ComplianceCheckRequest {
  project_id: string;
  check_type: "face_recognition" | "music_copyright" | "content_moderation";
  episode_number?: number;
  stage_type?: string;
}

export interface AsyncTaskResponse {
  task_id: string;
  status: string;
  message: string;
}

export interface ConsistencyCheck {
  id: string;
  project_id: string;
  check_type: string;
  episode_start: number;
  episode_end: number;
  status: "pending" | "completed" | "failed";
  issues_found: number;
  issues_detail: Record<string, any>;
  checked_at: string;
}

export interface ConsistencyCheckRequest {
  project_id: string;
  check_type: string;
  episode_start: number;
  episode_end: number;
}