/**
 * 阶段状态徽章
 */

import { Badge } from "@/components/ui/badge";
import { STAGE_STATUS_LABELS } from "@/lib/constants";
import { StageStatus } from "@/types";

interface StageStatusBadgeProps {
  status: StageStatus;
}

const VARIANT_MAP: Record<StageStatus, "default" | "secondary" | "destructive" | "outline"> = {
  [StageStatus.PENDING]: "outline",
  [StageStatus.READY]: "secondary",
  [StageStatus.GENERATING]: "secondary",
  [StageStatus.REVIEW]: "default",
  [StageStatus.APPROVED]: "default",
  [StageStatus.LOCKED]: "default",
};

export function StageStatusBadge({ status }: StageStatusBadgeProps) {
  return (
    <Badge variant={VARIANT_MAP[status] ?? "outline"} className="text-[10px]">
      {STAGE_STATUS_LABELS[status] ?? status}
    </Badge>
  );
}
