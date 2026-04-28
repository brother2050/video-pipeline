/**
 * 9阶段流水线总览页
 * - 横向时间线展示9个阶段
 * - 每个阶段节点显示名称、状态、候选数
 * - 点击跳转到 StageReview
 */

import { useParams, useNavigate } from "react-router-dom";
import { useProject } from "@/hooks/useProjects";
import { useStages } from "@/hooks/useStages";
import { useWebSocketStore } from "@/stores/websocketStore";
import { useEffect, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { StageStatusBadge } from "@/components/shared/StageStatusBadge";
import { ProjectNav } from "@/components/layout/ProjectNav";
import { STAGE_LABELS, STAGE_ORDER } from "@/lib/constants";
import { cn } from "@/lib/utils";
import { StageStatus, type StageProgressData } from "@/types";
import { CheckCircle, Clock, AlertCircle, Loader2 } from "lucide-react";

export default function PipelineView() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const subscribe = useWebSocketStore((s) => s.subscribe);
  const unsubscribe = useWebSocketStore((s) => s.unsubscribe);
  const lastMessage = useWebSocketStore((s) => s.lastMessage);

  const { data: project } = useProject(id || "");
  const { data: stages } = useStages(id || "");

  const [stageProgress, setStageProgress] = useState<Record<string, StageProgressData>>({});

  useEffect(() => {
    if (id) {
      subscribe(id);
    }
    return () => { 
      if (id) {
        unsubscribe(id);
      }
    };
  }, [id, subscribe, unsubscribe]);

  useEffect(() => {
    if (lastMessage?.type === "stage_progress") {
      const data = lastMessage.data as Record<string, unknown>;
      if (data.project_id === id && data.stage_type && data.progress_current !== undefined && data.progress_total !== undefined) {
        const progressData: StageProgressData = {
          project_id: String(data.project_id),
          stage_type: data.stage_type as any,
          progress_current: Number(data.progress_current),
          progress_total: Number(data.progress_total),
          status: String(data.status || "generating")
        };
        setStageProgress(prev => ({
          ...prev,
          [progressData.stage_type]: progressData
        }));
      }
    } else if (lastMessage?.type === "stage_status") {
      const data = lastMessage.data as Record<string, unknown>;
      if (data.project_id === id && data.stage_type && data.status) {
        // 重新获取阶段数据以更新状态
        queryClient.invalidateQueries({ queryKey: ["stages", id] });
        queryClient.invalidateQueries({ queryKey: ["stage", id, data.stage_type] });
      }
    }
  }, [lastMessage, id, queryClient]);

  if (!project || !stages) {
    return <div className="text-center py-12 text-muted-foreground">加载中...</div>;
  }

  const stageMap = new Map(stages.map((s) => [s.stage_type, s]));
  const summaryMap = new Map((project.stages_summary || []).map((s) => [s.stage_type, s]));

  const getStatusIcon = (status: StageStatus) => {
    switch (status) {
      case StageStatus.LOCKED: return <CheckCircle className="h-5 w-5 text-green-600" />;
      case StageStatus.APPROVED: return <CheckCircle className="h-5 w-5 text-green-500" />;
      case StageStatus.GENERATING: return <Loader2 className="h-5 w-5 text-yellow-500 animate-spin" />;
      case StageStatus.REVIEW: return <AlertCircle className="h-5 w-5 text-orange-500" />;
      case StageStatus.READY: return <Clock className="h-5 w-5 text-blue-500" />;
      default: return <Clock className="h-5 w-5 text-gray-400" />;
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">{project.name}</h1>
        <p className="text-sm text-muted-foreground mt-1">{project.description}</p>
        <div className="flex gap-2 mt-2">
          {project.genre && <span className="text-xs bg-secondary px-2 py-0.5 rounded">{project.genre}</span>}
          <span className="text-xs text-muted-foreground">{project.target_episodes} 集 · 每集 {project.target_duration_minutes} 分钟</span>
        </div>
      </div>

      <ProjectNav />

      <div className="relative">
        {/* 连接线 */}
        <div className="absolute top-8 left-4 right-4 h-0.5 bg-border z-0" />

        <div className="grid grid-cols-9 gap-2 relative z-10">
          {STAGE_ORDER.map((stageType, idx) => {
            const stage = stageMap.get(stageType);
            const status = stage?.status ?? StageStatus.PENDING;
            const isClickable = status !== StageStatus.PENDING;

            return (
              <div key={stageType} className="flex flex-col items-center">
                {/* 节点 */}
                <button
                  onClick={() => isClickable && navigate(`/projects/${id}/stages/${stageType}`)}
                  disabled={!isClickable}
                  className={cn(
                    "w-16 h-16 rounded-full border-2 flex items-center justify-center transition-all",
                    isClickable ? "cursor-pointer hover:scale-110 hover:shadow-md" : "cursor-default opacity-50",
                    status === StageStatus.LOCKED ? "border-green-500 bg-green-50" :
                    status === StageStatus.GENERATING ? "border-yellow-500 bg-yellow-50" :
                    status === StageStatus.REVIEW ? "border-orange-500 bg-orange-50" :
                    status === StageStatus.READY ? "border-blue-500 bg-blue-50" :
                    "border-gray-300 bg-gray-50"
                  )}
                >
                  {getStatusIcon(status)}
                </button>

                {/* 标签 */}
                <span className="text-xs font-medium mt-2 text-center">{STAGE_LABELS[stageType]}</span>
                <span className="text-[10px] text-muted-foreground">{idx + 1}/9</span>

                {/* 进度显示 */}
                {stageProgress[stageType] && (
                  <div className="mt-1 text-[10px] text-primary font-medium">
                    {stageProgress[stageType].progress_current}/{stageProgress[stageType].progress_total}
                  </div>
                )}

                {/* 候选数 */}
                {summaryMap.has(stageType) && summaryMap.get(stageType)!.has_candidates && (
                  <span className="text-[10px] text-muted-foreground mt-0.5">{summaryMap.get(stageType)!.candidate_count} 候选</span>
                )}

                {/* 状态标签 */}
                <StageStatusBadge status={status} />
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}