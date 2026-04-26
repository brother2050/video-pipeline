import { StageType, StageStatus } from "@/types";

export const STAGE_LABELS: Record<StageType, string> = {
  [StageType.WORLDBUILDING]: "世界观构建",
  [StageType.OUTLINE]: "大纲",
  [StageType.SCRIPT]: "剧本",
  [StageType.STORYBOARD]: "分镜",
  [StageType.KEYFRAME]: "关键帧",
  [StageType.VIDEO]: "视频",
  [StageType.AUDIO]: "音频",
  [StageType.ROUGH_CUT]: "粗剪",
  [StageType.FINAL_CUT]: "精剪",
};

export const STAGE_STATUS_LABELS: Record<StageStatus, string> = {
  [StageStatus.PENDING]: "待处理",
  [StageStatus.READY]: "就绪",
  [StageStatus.GENERATING]: "生成中",
  [StageStatus.REVIEW]: "审核中",
  [StageStatus.APPROVED]: "已通过",
  [StageStatus.LOCKED]: "已锁定",
};

export const STAGE_STATUS_COLORS: Record<StageStatus, string> = {
  [StageStatus.PENDING]: "bg-gray-100 text-gray-600",
  [StageStatus.READY]: "bg-blue-100 text-blue-700",
  [StageStatus.GENERATING]: "bg-yellow-100 text-yellow-700",
  [StageStatus.REVIEW]: "bg-orange-100 text-orange-700",
  [StageStatus.APPROVED]: "bg-green-100 text-green-700",
  [StageStatus.LOCKED]: "bg-purple-100 text-purple-700",
};

export const STAGE_ORDER: StageType[] = [
  StageType.WORLDBUILDING,
  StageType.OUTLINE,
  StageType.SCRIPT,
  StageType.STORYBOARD,
  StageType.KEYFRAME,
  StageType.VIDEO,
  StageType.AUDIO,
  StageType.ROUGH_CUT,
  StageType.FINAL_CUT,
];