/**
 * 阶段审核页 — 三栏布局
 * 左栏：阶段信息 + 提示词 + 生成参数 + 版本历史
 * 中栏：候选素材网格
 * 右栏：审核操作 + 回退
 */

import { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import { useProject } from "@/hooks/useProjects";
import {
  useStage, useCandidates, useGenerate, useSelectCandidate,
  useReview, useRollback, useVersions, useUpdatePrompt,
} from "@/hooks/useStages";
import { useWebSocketStore } from "@/stores/websocketStore";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { CandidateCard } from "@/components/shared/CandidateCard";
import { ReviewPanel } from "@/components/shared/ReviewPanel";
import { VersionTimeline } from "@/components/shared/VersionTimeline";
import { PromptEditor } from "@/components/shared/PromptEditor";
import { EmptyState } from "@/components/shared/EmptyState";
import { StageStatusBadge } from "@/components/shared/StageStatusBadge";
import { ProjectNav } from "@/components/layout/ProjectNav";
import { STAGE_LABELS } from "@/lib/constants";
import { Loader2, Play } from "lucide-react";
import { StageStatus, ReviewAction, StageType } from "@/types";
import type { ReviewRequest, RollbackRequest } from "@/types";

export default function StageReview() {
  const { id, stageType } = useParams<{ id: string; stageType: string }>();
  const subscribe = useWebSocketStore((s) => s.subscribe);
  const unsubscribe = useWebSocketStore((s) => s.unsubscribe);

  const { data: project } = useProject(id || "");
  const { data: stage, isLoading: stageLoading } = useStage(id || "", stageType || "");
  const { data: candidates } = useCandidates(id || "", stageType || "");
  const { data: versions } = useVersions(id || "", stageType || "");

  const generateMut = useGenerate(id || "", stageType || "");
  const selectMut = useSelectCandidate(id || "", stageType || "");
  const reviewMut = useReview(id || "", stageType || "");
  const rollbackMut = useRollback(id || "", stageType || "");
  const updatePromptMut = useUpdatePrompt(id || "", stageType || "");

  const [selectedCandidateId, setSelectedCandidateId] = useState<string | null>(null);
  const [numCandidates, setNumCandidates] = useState(3);

  useEffect(() => {
    if (id) subscribe(id);
    return () => { if (id) unsubscribe(id); };
  }, [id, subscribe, unsubscribe]);

  // 自动选中已锁定的候选
  useEffect(() => {
    if (stage?.current_candidate_id) {
      setSelectedCandidateId(stage.current_candidate_id);
    }
  }, [stage?.current_candidate_id]);

  if (stageLoading || !stage || !id || !stageType) {
    return <div className="text-center py-12 text-muted-foreground">加载中...</div>;
  }

  const isGenerating = stage.status === StageStatus.GENERATING;
  const isLocked = stage.status === StageStatus.LOCKED;

  // 可回退的阶段列表
  const allStageTypes: StageType[] = [
    StageType.WORLDBUILDING, StageType.OUTLINE, StageType.SCRIPT,
    StageType.STORYBOARD, StageType.KEYFRAME, StageType.VIDEO,
    StageType.AUDIO, StageType.ROUGH_CUT, StageType.FINAL_CUT,
  ];
  const currentIdx = allStageTypes.indexOf(stageType as StageType);
  const rollbackStages = allStageTypes.slice(0, currentIdx);

  const handleGenerate = async () => {
    await generateMut.mutateAsync({ num_candidates: numCandidates });
  };

  const handleSelect = (candidateId: string) => {
    setSelectedCandidateId(candidateId);
    selectMut.mutate(candidateId);
  };

  const handleReview = (data: ReviewRequest) => {
    reviewMut.mutate({
      ...data,
      candidate_id: data.action === ReviewAction.APPROVE ? (selectedCandidateId ?? undefined) : undefined,
    });
  };

  const handleRollback = (data: RollbackRequest) => {
    rollbackMut.mutate(data);
  };

  const handleCalculateImpact = async (target: StageType) => {
    const affectedStart = allStageTypes.indexOf(target);
    const affected = allStageTypes.slice(affectedStart);
    return {
      affected_stages: affected,
      message: `回退到 ${STAGE_LABELS[target]} 将重置以下阶段: ${affected.map(s => STAGE_LABELS[s]).join(", ")}`,
    };
  };

  return (
    <div className="space-y-4">
      {/* 顶部导航 */}
      <div>
        <p className="text-sm text-muted-foreground">{project?.name}</p>
        <ProjectNav />
      </div>

      {/* 三栏布局 */}
      <div className="grid grid-cols-[250px_1fr_220px] gap-4 h-[calc(100vh-220px)]">

        {/* 左栏 */}
        <Card className="p-4 overflow-y-auto space-y-4">
          <div>
            <h2 className="font-medium">{STAGE_LABELS[stageType as StageType]}</h2>
            <StageStatusBadge status={stage.status} />
          </div>

          <PromptEditor
            value={stage.prompt}
            onSave={(prompt) => updatePromptMut.mutate(prompt)}
            disabled={isLocked}
          />

          {/* 生成控制 */}
          {!isLocked && (
            <div className="space-y-2">
              <Label className="text-xs">候选数量</Label>
              <Input
                type="number"
                min={1}
                max={10}
                value={numCandidates}
                onChange={(e) => setNumCandidates(parseInt(e.target.value) || 3)}
                className="h-8"
              />
              <Button
                className="w-full"
                onClick={handleGenerate}
                disabled={isGenerating || generateMut.isPending}
              >
                {isGenerating || generateMut.isPending ? (
                  <><Loader2 className="h-4 w-4 mr-2 animate-spin" />生成中...</>
                ) : (
                  <><Play className="h-4 w-4 mr-2" />生成</>
                )}
              </Button>
            </div>
          )}

          {/* 版本历史 */}
          {versions && <VersionTimeline versions={versions} />}
        </Card>

        {/* 中栏 */}
        <div className="overflow-y-auto">
          {candidates && candidates.length > 0 ? (
            <div className="grid grid-cols-2 lg:grid-cols-3 gap-3">
              {candidates.map((c) => (
                <CandidateCard
                  key={c.id}
                  candidate={c}
                  stageType={stageType as StageType}
                  projectId={id}
                  isSelected={selectedCandidateId === c.id}
                  onSelect={() => handleSelect(c.id)}
                />
              ))}
            </div>
          ) : (
            <EmptyState
              title="暂无候选素材"
              description={isLocked ? "此阶段已锁定" : "点击左侧生成按钮开始创作"}
            />
          )}
        </div>

        {/* 右栏 */}
        <Card className="p-4 overflow-y-auto">
          <ReviewPanel
            hasSelectedCandidate={!!selectedCandidateId}
            onReview={handleReview}
            onRollback={handleRollback}
            onCalculateImpact={handleCalculateImpact}
            availableRollbackStages={rollbackStages}
            isReviewing={reviewMut.isPending || rollbackMut.isPending}
          />
        </Card>
      </div>
    </div>
  );
}