import type { WorkflowAnalysis } from "@/types";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface WorkflowAnalysisViewProps {
  analysis: WorkflowAnalysis;
}

export function WorkflowAnalysisView({ analysis }: WorkflowAnalysisViewProps) {
  return (
    <Card className="p-4 space-y-3">
      <div className="flex items-center justify-between">
        <h4 className="text-sm font-medium">工作流分析结果</h4>
        <div className="flex gap-2">
          <Badge variant="outline">{analysis.total_nodes} 节点</Badge>
          {analysis.is_video_workflow && <Badge variant="secondary">视频工作流</Badge>}
        </div>
      </div>

      {analysis.checkpoint_nodes.length > 0 && (
        <div>
          <p className="text-xs font-medium text-muted-foreground mb-1">模型</p>
          {analysis.checkpoint_nodes.map((n) => (
            <div key={n.id} className="text-xs">#{n.id} {n.class_type} → {n.model}</div>
          ))}
        </div>
      )}

      {analysis.positive_text_nodes.length > 0 && (
        <div>
          <p className="text-xs font-medium text-muted-foreground mb-1">正向提示词</p>
          {analysis.positive_text_nodes.map((n) => (
            <div key={n.id} className="text-xs truncate">#{n.id} &quot;{n.text_preview}&quot;</div>
          ))}
        </div>
      )}

      {analysis.negative_text_nodes.length > 0 && (
        <div>
          <p className="text-xs font-medium text-muted-foreground mb-1">负向提示词</p>
          {analysis.negative_text_nodes.map((n) => (
            <div key={n.id} className="text-xs truncate">#{n.id} &quot;{n.text_preview}&quot;</div>
          ))}
        </div>
      )}

      {analysis.sampler_nodes.length > 0 && (
        <div>
          <p className="text-xs font-medium text-muted-foreground mb-1">采样器</p>
          {analysis.sampler_nodes.map((n) => (
            <div key={n.id} className="text-xs">
              #{n.id} steps={n.steps} cfg={n.cfg} sampler={n.sampler}
            </div>
          ))}
        </div>
      )}

      {analysis.latent_nodes.length > 0 && (
        <div>
          <p className="text-xs font-medium text-muted-foreground mb-1">尺寸</p>
          {analysis.latent_nodes.map((n) => (
            <div key={n.id} className="text-xs">
              #{n.id} {n.width}x{n.height} {n.is_video ? "(视频)" : ""}
            </div>
          ))}
        </div>
      )}

      <div>
        <p className="text-xs font-medium text-muted-foreground mb-1">可覆盖参数</p>
        <div className="flex flex-wrap gap-1">
          {Object.entries(analysis.overridable_params).filter(([, v]) => v).map(([k]) => (
            <Badge key={k} variant="outline" className="text-[10px]">{k.replace("has_", "")}</Badge>
          ))}
        </div>
      </div>
    </Card>
  );
}
