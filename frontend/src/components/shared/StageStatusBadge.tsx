/**
 * 阶段状态徽章
 */

import { Badge } from "@/components/ui/badge";
import { STAGE_STATUS_LABELS, STAGE_STATUS_COLORS } from "@/lib/constants";
import { StageStatus } from "@/types";

interface StageStatusBadgeProps {
  status: StageStatus;
}

export function StageStatusBadge({ status }: StageStatusBadgeProps) {
  return (
    <Badge variant="outline" className={STAGE_STATUS_COLORS[status] ?? "bg-gray-100 text-gray-600"}>
      {STAGE_STATUS_LABELS[status] ?? status}
    </Badge>
  );
}