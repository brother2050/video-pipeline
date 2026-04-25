import type {
  StageType,
  StageStatus,
  ReviewAction,
  SupplierCapability,
  NodeStatus,
  FileType,
} from "./enums";

// --- 通用 ---
export interface APIResponse<T> {
  success: boolean;
  data: T | null;
  message: string | null;
}

export interface PaginatedData<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

export interface WSMessage {
  type: string;
  data: Record<string, unknown>;
  timestamp: string;
}

// --- 项目 ---
export interface ProjectCreate {
  name: string;
  description?: string;
  genre?: string;
  target_episodes?: number;
  target_duration_minutes?: number;
}

export interface ProjectUpdate {
  name?: string;
  description?: string;
  genre?: string;
  target_episodes?: number;
  target_duration_minutes?: number;
}

export interface StageSummary {
  stage_type: StageType;
  status: StageStatus;
  has_candidates: boolean;
  candidate_count: number;
}

export interface ProjectResponse {
  id: string;
  name: string;
  description: string;
  genre: string;
  target_episodes: number;
  target_duration_minutes: number;
  current_stage: StageType;
  status: string;
  stages_summary: StageSummary[];
  created_at: string;
  updated_at: string;
}

export interface ProjectDetail extends ProjectResponse {
  stages: StageResponse[];
}

// --- 项目设置 ---
export interface ProjectSettingResponse {
  id: string;
  project_id: string;

  // 生成默认值
  default_num_candidates: number;
  image_width: number;
  image_height: number;
  video_resolution: string;
  video_fps: number;
  video_duration_sec: number;

  // 音频默认值
  default_tts_voice: string;
  default_bgm_style: string;
  default_sfx_library: string;

  // 输出设置
  output_bitrate: string;
  output_audio_codec: string;
  output_audio_bitrate: string;

  // 字幕设置
  subtitle_enabled: boolean;
  subtitle_font: string;
  subtitle_size: number;
  subtitle_color: string;
  subtitle_position: string;

  // 调色设置
  color_grade_lut: string;
  color_grade_intensity: number;
  vignette_intensity: number;
  grain_intensity: number;

  // 供应商偏好
  preferred_suppliers: Record<string, string>;

  // ComfyUI
  comfyui_workflow_path: string;

  // 扩展
  extra: Record<string, unknown>;

  created_at: string;
  updated_at: string;
}

export interface ProjectSettingUpdate {
  default_num_candidates?: number;
  image_width?: number;
  image_height?: number;
  video_resolution?: string;
  video_fps?: number;
  video_duration_sec?: number;

  default_tts_voice?: string;
  default_bgm_style?: string;
  default_sfx_library?: string;

  output_bitrate?: string;
  output_audio_codec?: string;
  output_audio_bitrate?: string;

  subtitle_enabled?: boolean;
  subtitle_font?: string;
  subtitle_size?: number;
  subtitle_color?: string;
  subtitle_position?: string;

  color_grade_lut?: string;
  color_grade_intensity?: number;
  vignette_intensity?: number;
  grain_intensity?: number;

  preferred_suppliers?: Record<string, string>;
  comfyui_workflow_path?: string;
  extra?: Record<string, unknown>;
}

// --- 阶段 ---
export interface StageResponse {
  id: string;
  project_id: string;
  stage_type: StageType;
  status: StageStatus;
  prompt: string;
  config: Record<string, unknown>;
  current_candidate_id: string | null;
  locked_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface StageGenerateRequest {
  prompt?: string;
  config?: Record<string, unknown>;
  num_candidates?: number;
}

export interface StagePromptUpdate {
  prompt: string;
}

export interface StageConfigUpdate {
  config: Record<string, unknown>;
}

// --- 候选与素材 ---
export interface ArtifactResponse {
  id: string;
  candidate_id: string;
  file_type: FileType;
  file_path: string;
  file_url: string;
  file_size: number;
  mime_type: string;
  metadata: Record<string, unknown>;
  created_at: string;
}

export interface CandidateResponse {
  id: string;
  stage_id: string;
  stage_type: StageType;
  content: Record<string, unknown>;
  artifacts: ArtifactResponse[];
  metadata: Record<string, unknown>;
  is_selected: boolean;
  created_at: string;
}

export interface CandidateSelectRequest {
  candidate_id: string;
}

// --- 审核与回退 ---
export interface ReviewRequest {
  action: ReviewAction;
  comment?: string;
  candidate_id?: string;
}

export interface RollbackRequest {
  target_stage: StageType;
  reason?: string;
}

export interface RollbackResponse {
  affected_stages: StageType[];
  message: string;
}

// --- 版本 ---
export interface VersionResponse {
  id: string;
  stage_id: string;
  version_number: number;
  content_snapshot: Record<string, unknown>;
  prompt_snapshot: string;
  diff_summary: string | null;
  created_at: string;
  created_by: string;
}

// --- 节点 ---
export interface NodeCreate {
  name: string;
  host: string;
  port: number;
  capabilities: SupplierCapability[];
  models?: string[];
  tags?: Record<string, string>;
}

export interface NodeUpdate {
  name?: string;
  host?: string;
  port?: number;
  capabilities?: SupplierCapability[];
  models?: string[];
  tags?: Record<string, string>;
}

export interface NodeResponse {
  id: string;
  name: string;
  host: string;
  port: number;
  capabilities: SupplierCapability[];
  models: string[];
  tags: Record<string, string>;
  status: NodeStatus;
  last_heartbeat: string | null;
  created_at: string;
  updated_at: string;
}

export interface NodeToggleRequest {
  enabled: boolean;
}

export interface NodeHealthResponse {
  status: string;
  latency_ms: number;
  models_loaded: string[];
}

// --- 供应商 ---
export interface SupplierSlot {
  provider: string;
  model?: string;
  base_url?: string;
  api_key?: string;
  is_local?: boolean;
  priority?: number;
  extra_params?: Record<string, unknown>;
}

export interface CapabilityConfigResponse {
  capability: SupplierCapability;
  suppliers: SupplierSlot[];
  retry_count: number;
  timeout_seconds: number;
  local_timeout_seconds: number;
}

export interface CapabilityConfigUpdate {
  suppliers?: SupplierSlot[];
  retry_count?: number;
  timeout_seconds?: number;
  local_timeout_seconds?: number;
}

export interface SupplierTestRequest {
  capability: SupplierCapability;
  slot: SupplierSlot;
  test_prompt?: string;
}

export interface SupplierTestResponse {
  success: boolean;
  latency_ms: number;
  response_preview: string | null;
  error: string | null;
}

// --- 系统 ---
export interface SystemStatus {
  total_projects: number;
  active_projects: number;
  total_nodes: number;
  online_nodes: number;
  supplier_health: Record<string, string>;
  uptime_seconds: number;
}

// --- 工作流分析（ComfyUI） ---
export interface WorkflowNodeInfo {
  id: string;
  class_type: string;
  text_preview?: string;
  steps?: number;
  cfg?: number;
  sampler?: string;
  width?: number;
  height?: number;
  is_video?: boolean;
  model?: string;
  image?: string;
  prefix?: string;
}

export interface WorkflowAnalysis {
  total_nodes: number;
  positive_text_nodes: WorkflowNodeInfo[];
  negative_text_nodes: WorkflowNodeInfo[];
  sampler_nodes: WorkflowNodeInfo[];
  latent_nodes: WorkflowNodeInfo[];
  checkpoint_nodes: WorkflowNodeInfo[];
  load_image_nodes: WorkflowNodeInfo[];
  save_nodes: WorkflowNodeInfo[];
  is_video_workflow: boolean;
  overridable_params: {
    has_positive: boolean;
    has_negative: boolean;
    has_sampler: boolean;
    has_latent: boolean;
    has_checkpoint: boolean;
    has_load_image: boolean;
    has_video_frames: boolean;
  };
}