import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { useNavigate } from "react-router-dom";
import { Eye } from "lucide-react";
import type { CandidateResponse } from "@/types";

interface CandidateCardProps {
  candidate: CandidateResponse;
  stageType: string;
  projectId: string;
  isSelected: boolean;
  onSelect: () => void;
}

export function CandidateCard({ candidate, stageType, projectId, isSelected, onSelect }: CandidateCardProps) {
  const navigate = useNavigate();
  const contentPreview = JSON.stringify(candidate.content, null, 2).slice(0, 200);

  const handleClick = () => {
    console.log('CandidateCard clicked:', {
      candidateId: candidate.id,
      artifacts: candidate.artifacts,
      artifactsCount: candidate.artifacts?.length || 0,
      stageType,
      projectId
    });
    
    // 点击卡片主体时调用onSelect进行选中（用于审核）
    onSelect();
  };

  const handleViewDetail = (e: React.MouseEvent) => {
    e.stopPropagation();
    const targetPath = `/projects/${projectId}/stages/${stageType}/candidates/${candidate.id}`;
    console.log('Navigating to:', targetPath);
    navigate(targetPath);
  };

  return (
    <Card
      className={cn(
        "p-3 transition-all hover:shadow-md",
        isSelected && "ring-2 ring-primary"
      )}
      onClick={handleClick}
    >
      <div className="flex items-start justify-between mb-2">
        <Badge variant="outline" className="text-[10px]">
          #{((candidate.metadata?.candidate_index as number) ?? 0) + 1}
        </Badge>
        <div className="flex items-center gap-2">
          {isSelected && <Badge className="text-[10px]">已选中</Badge>}
          <Button 
            variant="ghost" 
            size="sm" 
            className="h-6 px-2 text-[10px]"
            onClick={handleViewDetail}
            title="查看详情"
          >
            <Eye className="h-3 w-3" />
          </Button>
        </div>
      </div>
      <div className="text-xs text-muted-foreground line-clamp-4 whitespace-pre-wrap">
        {contentPreview}
      </div>
      {candidate.artifacts.length > 0 && (
        <div className="mt-2 text-[10px] text-muted-foreground">
          {candidate.artifacts.length} 个素材文件
        </div>
      )}
    </Card>
  );
}