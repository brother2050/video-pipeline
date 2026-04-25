/**
 * 审核操作面板
 */

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { ReviewAction, StageType } from "@/types";
import type { ReviewRequest, RollbackRequest } from "@/types";
import { CheckCircle, XCircle, RotateCcw, AlertTriangle, Loader2 } from "lucide-react";
import { STAGE_LABELS } from "@/lib/constants";

interface ReviewPanelProps {
  hasSelectedCandidate: boolean;
  onReview: (data: ReviewRequest) => void;
  onRollback: (data: RollbackRequest) => void;
  onCalculateImpact: (target: StageType) => Promise<{ affected_stages: StageType[]; message: string }>;
  availableRollbackStages: StageType[];
  isReviewing: boolean;
}

export function ReviewPanel({
  hasSelectedCandidate,
  onReview,
  onRollback,
  onCalculateImpact,
  availableRollbackStages,
  isReviewing,
}: ReviewPanelProps) {
  const [comment, setComment] = useState("");
  const [rollbackTarget, setRollbackTarget] = useState<string>("");
  const [impactPreview, setImpactPreview] = useState<string | null>(null);

  const handleRollbackPreview = async (target: StageType) => {
    setRollbackTarget(target);
    const impact = await onCalculateImpact(target);
    setImpactPreview(impact.message);
  };

  return (
    <div className="space-y-4">
      <h3 className="text-sm font-medium">审核操作</h3>

      {/* 评论 */}
      <div>
        <Label className="text-xs">审核意见（可选）</Label>
        <Textarea
          value={comment}
          onChange={(e) => setComment(e.target.value)}
          placeholder="输入审核意见..."
          rows={3}
          className="text-sm"
        />
      </div>

      {/* 通过 / 拒绝 */}
      <div className="flex gap-2">
        <Button
          className="flex-1"
          disabled={!hasSelectedCandidate || isReviewing}
          onClick={() => onReview({ action: ReviewAction.APPROVE, comment })}
        >
          {isReviewing ? <Loader2 className="h-4 w-4 mr-1 animate-spin" /> : <CheckCircle className="h-4 w-4 mr-1" />}
          通过
        </Button>
        <Button
          variant="outline"
          className="flex-1"
          disabled={isReviewing}
          onClick={() => onReview({ action: ReviewAction.REJECT, comment })}
        >
          <XCircle className="h-4 w-4 mr-1" />
          拒绝
        </Button>
      </div>

      {/* 回退 */}
      {availableRollbackStages.length > 0 && (
        <div className="border-t pt-4 space-y-2">
          <Label className="text-xs font-medium flex items-center gap-1">
            <RotateCcw className="h-3 w-3" />
            回退到之前的阶段
          </Label>
          <Select value={rollbackTarget} onValueChange={(v) => handleRollbackPreview(v as StageType)}>
            <SelectTrigger className="h-8 text-xs">
              <SelectValue placeholder="选择回退目标" />
            </SelectTrigger>
            <SelectContent>
              {availableRollbackStages.map((s) => (
                <SelectItem key={s} value={s}>{STAGE_LABELS[s]}</SelectItem>
              ))}
            </SelectContent>
          </Select>

          {impactPreview && (
            <div className="flex items-start gap-2 p-2 bg-yellow-50 border border-yellow-200 rounded text-xs">
              <AlertTriangle className="h-3.5 w-3.5 text-yellow-600 mt-0.5 shrink-0" />
              <span className="text-yellow-800">{impactPreview}</span>
            </div>
          )}

          <Button
            variant="destructive"
            size="sm"
            className="w-full"
            disabled={!rollbackTarget || isReviewing}
            onClick={() => onRollback({ target_stage: rollbackTarget as StageType, reason: comment })}
          >
            确认回退
          </Button>
        </div>
      )}
    </div>
  );
}
