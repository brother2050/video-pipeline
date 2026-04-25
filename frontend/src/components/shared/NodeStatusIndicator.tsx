/**
 * 节点状态指示器
 */

import { cn } from "@/lib/utils";
import { NodeStatus } from "@/types";

interface NodeStatusIndicatorProps {
  status: NodeStatus;
}

const STATUS_CONFIG: Record<NodeStatus, { label: string; color: string }> = {
  [NodeStatus.ONLINE]: { label: "在线", color: "bg-green-500" },
  [NodeStatus.OFFLINE]: { label: "离线", color: "bg-gray-400" },
  [NodeStatus.BUSY]: { label: "忙碌", color: "bg-yellow-500" },
  [NodeStatus.ERROR]: { label: "错误", color: "bg-red-500" },
};

export function NodeStatusIndicator({ status }: NodeStatusIndicatorProps) {
  const config = STATUS_CONFIG[status] ?? STATUS_CONFIG[NodeStatus.OFFLINE];
  return (
    <div className="flex items-center gap-1.5">
      <span className={cn("h-2 w-2 rounded-full", config.color)} />
      <span className="text-xs">{config.label}</span>
    </div>
  );
}
