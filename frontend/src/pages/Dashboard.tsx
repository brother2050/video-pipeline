/**
 * 仪表板页面
 * - 系统状态卡片：项目总数、活跃数、在线节点数、供应商健康
 * - 最近 5 个项目列表
 * - 快速新建项目按钮
 */

import { useNavigate } from "react-router-dom";
import { useSystemStatus } from "@/hooks/useApi";
import { useProjects } from "@/hooks/useProjects";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { StageStatusBadge } from "@/components/shared/StageStatusBadge";
import { EmptyState } from "@/components/shared/EmptyState";
import { formatDate } from "@/lib/utils";
import { STAGE_LABELS } from "@/lib/constants";
import { FolderPlus, Film, Server, Activity } from "lucide-react";
import { StageStatus } from "@/types";

export default function Dashboard() {
  const navigate = useNavigate();
  const { data: status } = useSystemStatus();
  const { data: projects } = useProjects(1, 5);

  const statCards = [
    { label: "项目总数", value: status?.total_projects ?? "—", icon: Film },
    { label: "活跃项目", value: status?.active_projects ?? "—", icon: Activity },
    { label: "在线节点", value: status ? `${status.online_nodes}/${status.total_nodes}` : "—", icon: Server },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">仪表板</h1>
        <Button onClick={() => navigate("/projects")}>
          <FolderPlus className="h-4 w-4 mr-2" />
          新建项目
        </Button>
      </div>

      {/* 状态卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {statCards.map((card) => (
          <Card key={card.label} className="p-4 flex items-center gap-4">
            <card.icon className="h-8 w-8 text-muted-foreground" />
            <div>
              <p className="text-2xl font-bold">{card.value}</p>
              <p className="text-sm text-muted-foreground">{card.label}</p>
            </div>
          </Card>
        ))}
      </div>

      {/* 供应商健康 */}
      {status && Object.keys(status.supplier_health).length > 0 && (
        <Card className="p-4">
          <h3 className="text-sm font-medium mb-3">供应商状态</h3>
          <div className="flex flex-wrap gap-2">
            {Object.entries(status.supplier_health).map(([cap, health]) => (
              <Badge key={cap} variant={health === "ok" ? "default" : health === "degraded" ? "secondary" : "destructive"}>
                {cap}: {health}
              </Badge>
            ))}
          </div>
        </Card>
      )}

      {/* 最近项目 */}
      <div>
        <h2 className="text-lg font-medium mb-3">最近项目</h2>
        {projects && projects.items.length > 0 ? (
          <div className="space-y-2">
            {projects.items.map((p) => (
              <Card
                key={p.id}
                className="p-4 cursor-pointer hover:bg-accent/50 transition-colors"
                onClick={() => navigate(`/projects/${p.id}/pipeline`)}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-medium">{p.name}</h3>
                    <p className="text-sm text-muted-foreground truncate max-w-md">{p.description}</p>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-xs text-muted-foreground">
                      {STAGE_LABELS[p.current_stage]}
                    </span>
                    <StageStatusBadge status={p.stages_summary.find(s => s.stage_type === p.current_stage)?.status ?? StageStatus.PENDING} />
                    <span className="text-xs text-muted-foreground">{formatDate(p.updated_at)}</span>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        ) : (
          <EmptyState title="暂无项目" description="点击右上角按钮创建第一个项目" />
        )}
      </div>
    </div>
  );
}
