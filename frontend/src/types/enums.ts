export enum StageType {
  WORLDBUILDING = "worldbuilding",
  OUTLINE = "outline",
  SCRIPT = "script",
  STORYBOARD = "storyboard",
  KEYFRAME = "keyframe",
  VIDEO = "video",
  AUDIO = "audio",
  ROUGH_CUT = "rough_cut",
  FINAL_CUT = "final_cut",
}

export enum StageStatus {
  PENDING = "pending",
  READY = "ready",
  GENERATING = "generating",
  REVIEW = "review",
  APPROVED = "approved",
  LOCKED = "locked",
}

export enum ReviewAction {
  APPROVE = "approve",
  REJECT = "reject",
  REGENERATE = "regenerate",
}

export enum SupplierCapability {
  LLM = "llm",
  IMAGE = "image",
  VIDEO = "video",
  TTS = "tts",
  BGM = "bgm",
  SFX = "sfx",
  POST = "post",
}

export enum NodeStatus {
  ONLINE = "online",
  OFFLINE = "offline",
  BUSY = "busy",
  ERROR = "error",
}

export enum FileType {
  TEXT = "text",
  IMAGE = "image",
  VIDEO = "video",
  AUDIO = "audio",
  JSON_DATA = "json",
}
