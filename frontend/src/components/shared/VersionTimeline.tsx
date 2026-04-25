/**
 * 版本时间线组件
 */

import { formatDate } from "@/lib/utils";
import type { VersionResponse } from "@/types";
import { GitBranch } from "lucide-react";

interface VersionTimelineProps {
  versions: VersionResponse[];
}

export function VersionTimeline({ versions }: VersionTimelineProps) {
  if (versions.length === 0) return null;

  return (
    <div className="space-y-2">
      <h4 className="text-xs font-medium text-muted-foreground">版本历史</h4>
      <div className="space-y-1 max-h-48 overflow-y-auto">
        {versions.map((v) => (
          <div key={v.id} className="flex items-start gap-2 text-[10px]">
            <GitBranch className="h-3 w-3 text-muted-foreground mt-0.5 shrink-0" />
            <div>
              <span className="font-medium">v{v.version_number}</span>
              <span className="text-muted-foreground ml-1">{v.diff_summary || "变更"}</span>
              <span className="text-muted-foreground ml-1">{formatDate(v.created_at)}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
