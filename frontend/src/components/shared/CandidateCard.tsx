import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import type { CandidateResponse } from "@/types";

interface CandidateCardProps {
  candidate: CandidateResponse;
  stageType: string;
  isSelected: boolean;
  onSelect: () => void;
}

export function CandidateCard({ candidate, isSelected, onSelect }: CandidateCardProps) {
  const contentPreview = JSON.stringify(candidate.content, null, 2).slice(0, 200);

  return (
    <Card
      className={cn(
        "p-3 cursor-pointer transition-all hover:shadow-md",
        isSelected && "ring-2 ring-primary"
      )}
      onClick={onSelect}
    >
      <div className="flex items-start justify-between mb-2">
        <Badge variant="outline" className="text-[10px]">
          #{((candidate.metadata?.candidate_index as number) ?? 0) + 1}
        </Badge>
        {isSelected && <Badge className="text-[10px]">已选中</Badge>}
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
