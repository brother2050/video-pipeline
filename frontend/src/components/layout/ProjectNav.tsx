/**
 * 项目导航栏 — 显示在项目详情页顶部
 */

import { useParams, useNavigate, useLocation } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const NAV_ITEMS = [
  { label: "流水线", path: "pipeline" },
  { label: "角色状态", path: "characters" },
  { label: "场景资产", path: "scenes" },
  { label: "节奏模板", path: "pacing" },
  { label: "合规检查", path: "compliance" },
  { label: "设置", path: "settings" },
];

export function ProjectNav() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const location = useLocation();

  const currentSegment = location.pathname.split("/").pop() ?? "";

  return (
    <nav className="flex gap-1 border-b pb-2">
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
    </nav>
  );
}