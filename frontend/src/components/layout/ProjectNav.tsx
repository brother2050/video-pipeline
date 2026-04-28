/**
 * 项目导航栏 — 显示在项目详情页顶部
 * 集成角色状态、场景资产、节奏模板、合规检查到流水线中
 */

import { useParams, useNavigate, useLocation } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const NAV_ITEMS = [
  { label: "流水线", path: "pipeline", description: "9阶段视频制作流程" },
  { label: "角色状态", path: "characters", description: "世界观阶段集成" },
  { label: "场景资产", path: "scenes", description: "分镜阶段集成" },
  { label: "节奏模板", path: "pacing", description: "剧情大纲阶段集成" },
  { label: "合规检查", path: "compliance", description: "全流程合规监控" },
  { label: "设置", path: "settings", description: "项目配置" },
];

export function ProjectNav() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const location = useLocation();

  const currentSegment = location.pathname.split("/").pop() ?? "";

  return (
    <nav className="flex flex-col gap-2 border-b pb-4">
      <div className="flex gap-1">
        {NAV_ITEMS.map((item) => (
          <Button
            key={item.path}
            variant="ghost"
            size="sm"
            className={cn(
              "text-sm",
              currentSegment === item.path && "bg-accent text-accent-foreground"
            )}
            onClick={() => navigate(`/projects/${id}/${item.path}`)}
          >
            {item.label}
          </Button>
        ))}
      </div>
      <div className="text-xs text-muted-foreground">
        {NAV_ITEMS.find(item => item.path === currentSegment)?.description || ""}
      </div>
    </nav>
  );
}