import { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useCandidateDetail, useStages } from "@/hooks/useStages";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ArrowLeft, Download, ZoomIn, ZoomOut, RotateCw, Play } from "lucide-react";
import { STAGE_LABELS, STAGE_ORDER } from "@/lib/constants";
import { StageStatus } from "@/types";
import { StageStatusBadge } from "@/components/shared/StageStatusBadge";
import { cn } from "@/lib/utils";

export default function CandidateDetailView() {
  const { id: projectId, stageType, candidateId } = useParams<{
    id: string;
    stageType: string;
    candidateId: string;
  }>();
  const navigate = useNavigate();
  const { data: candidate, isLoading } = useCandidateDetail(projectId || "", stageType || "", candidateId || "");
  const { data: stages } = useStages(projectId || "");

  console.log('CandidateDetailView rendered:', {
    projectId,
    stageType,
    candidateId,
    candidate,
    isLoading
  });

  const [zoom, setZoom] = useState(1);
  const [rotation, setRotation] = useState(0);
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);

  const handleZoomIn = () => setZoom(prev => Math.min(prev + 0.25, 3));
  const handleZoomOut = () => setZoom(prev => Math.max(prev - 0.25, 0.5));
  const handleRotate = () => setRotation(prev => (prev + 90) % 360);

  const handleNextImage = () => {
    if (candidate && candidate.artifacts) {
      setCurrentImageIndex(prev => (prev + 1) % candidate.artifacts.length);
    }
  };

  const handlePrevImage = () => {
    if (candidate && candidate.artifacts) {
      setCurrentImageIndex(prev => (prev - 1 + candidate.artifacts.length) % candidate.artifacts.length);
    }
  };

  const handleDownload = async (artifact: any) => {
    try {
      const response = await fetch(`/api/files/${artifact.file_path}`);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = artifact.file_path.split('/').pop();
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Download failed:', error);
    }
  };

  const getMediaDescription = (artifact: any, candidateData: any) => {
    if (!candidateData || !candidateData.content || !candidateData.content.generated_images) {
      return null;
    }

    const generatedImages = candidateData.content.generated_images;
    const imageData = generatedImages.find((img: any) => img.artifact_id === artifact.id);
    
    if (!imageData) return null;

    return {
      shotRef: imageData.shot_ref,
      prompt: imageData.prompt_used,
      negativePrompt: imageData.negative_prompt_used,
      width: imageData.width,
      height: imageData.height,
    };
  };

  const getMediaComponent = (artifact: any) => {
    const fileType = artifact.file_type;
    
    if (fileType === 'image') {
      return (
        <div className="flex items-center justify-center bg-black/5 rounded-lg overflow-hidden">
          <img
            src={`/api/files/${artifact.file_path}`}
            alt={`Artifact ${artifact.id}`}
            className="max-w-full max-h-[70vh] object-contain transition-transform"
            style={{
              transform: `scale(${zoom}) rotate(${rotation}deg)`,
            }}
          />
        </div>
      );
    } else if (fileType === 'video') {
      return (
        <div className="flex items-center justify-center bg-black/5 rounded-lg overflow-hidden">
          <video
            src={`/api/files/${artifact.file_path}`}
            controls
            className="max-w-full max-h-[70vh]"
            autoPlay={isPlaying}
            onPlay={() => setIsPlaying(true)}
            onPause={() => setIsPlaying(false)}
          />
        </div>
      );
    } else if (fileType === 'audio') {
      return (
        <div className="flex items-center justify-center bg-black/5 rounded-lg p-8">
          <audio
            src={`/api/files/${artifact.file_path}`}
            controls
            className="w-full max-w-2xl"
            onPlay={() => setIsPlaying(true)}
            onPause={() => setIsPlaying(false)}
          />
          <div className="mt-4 text-center text-muted-foreground">
            <Play className="h-16 w-16 mx-auto mb-2" />
            <p>音频文件</p>
          </div>
        </div>
      );
    }
    
    return (
      <div className="flex items-center justify-center bg-black/5 rounded-lg p-8">
        <p className="text-muted-foreground">不支持的文件类型: {fileType}</p>
      </div>
    );
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">加载中...</p>
        </div>
      </div>
    );
  }

  if (!candidate) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Card className="p-8 max-w-md">
          <p className="text-center text-muted-foreground mb-4">未找到候选详情</p>
          <Button onClick={() => navigate(-1)}>返回</Button>
        </Card>
      </div>
    );
  }

  const artifacts = candidate.artifacts || [];
  const currentArtifact = artifacts[currentImageIndex];

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto py-6 px-4">
        {/* 流水线节点导航 */}
        <Card className="mb-6 p-4">
          <h3 className="text-sm font-semibold mb-3 text-muted-foreground">流水线节点</h3>
          <div className="flex items-center gap-2 overflow-x-auto pb-2">
            {STAGE_ORDER.map((stage) => {
              const stageData = stages?.find(s => s.stage_type === stage);
              const isActive = stage === stageType;
              const isClickable = stageData?.status !== StageStatus.PENDING;
              
              const handleStageClick = () => {
                console.log('Stage clicked:', {
                  stage,
                  isClickable,
                  projectId,
                  stageData,
                  currentCandidateId: stageData?.current_candidate_id
                });
                
                if (!isClickable || !projectId) return;
                
                // 跳转到阶段审核页面
                console.log('Navigating to stage review:', `/projects/${projectId}/stages/${stage}`);
                navigate(`/projects/${projectId}/stages/${stage}`);
              };
              
              return (
                <button
                  key={stage}
                  onClick={handleStageClick}
                  disabled={!isClickable}
                  className={cn(
                    "flex-shrink-0 px-3 py-2 rounded-lg border-2 transition-all text-sm font-medium",
                    isActive 
                      ? "border-primary bg-primary/10 text-primary" 
                      : "border-border bg-background hover:border-primary/50 hover:bg-primary/5",
                    !isClickable && "opacity-50 cursor-not-allowed"
                  )}
                >
                  <div className="flex flex-col items-center">
                    <span className="text-xs">{STAGE_LABELS[stage]}</span>
                    <StageStatusBadge status={stageData?.status ?? StageStatus.PENDING} />
                  </div>
                </button>
              );
            })}
          </div>
        </Card>

        <div className="flex items-center justify-between mb-6">
          <Button variant="ghost" onClick={() => navigate(-1)}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            返回审核
          </Button>
          
          <div className="flex gap-2">
            <Button variant="outline" size="sm" onClick={handleZoomOut} disabled={zoom <= 0.5}>
              <ZoomOut className="h-4 w-4" />
            </Button>
            <Button variant="outline" size="sm" onClick={handleZoomIn} disabled={zoom >= 3}>
              <ZoomIn className="h-4 w-4" />
            </Button>
            <Button variant="outline" size="sm" onClick={handleRotate}>
              <RotateCw className="h-4 w-4" />
            </Button>
            {currentArtifact && (
              <Button variant="outline" size="sm" onClick={() => handleDownload(currentArtifact)}>
                <Download className="h-4 w-4" />
              </Button>
            )}
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <Card className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold">媒体内容</h2>
                {artifacts.length > 1 && (
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <span>{currentImageIndex + 1} / {artifacts.length}</span>
                    <Button variant="outline" size="sm" onClick={handlePrevImage}>
                      ←
                    </Button>
                    <Button variant="outline" size="sm" onClick={handleNextImage}>
                      →
                    </Button>
                  </div>
                )}
              </div>

              <div className="flex items-center justify-center min-h-[60vh] bg-muted/30 rounded-lg">
                {currentArtifact ? getMediaComponent(currentArtifact) : (
                  <div className="w-full p-6">
                    {artifacts.length === 0 && candidate.content ? (
                      <div className="text-left">
                        <h3 className="text-lg font-semibold mb-4">候选内容</h3>
                        <pre className="text-sm whitespace-pre-wrap bg-background p-4 rounded-lg border overflow-auto max-h-[50vh]">
                          {JSON.stringify(candidate.content, null, 2)}
                        </pre>
                      </div>
                    ) : (
                      <p className="text-muted-foreground">暂无媒体文件</p>
                    )}
                  </div>
                )}
              </div>

              {currentArtifact && (() => {
                const description = getMediaDescription(currentArtifact, candidate);
                if (!description) return null;
                
                return (
                  <Card className="mt-4 p-4 bg-muted/50">
                    <h4 className="text-sm font-semibold mb-3 text-muted-foreground">媒体描述</h4>
                    <div className="space-y-2 text-sm">
                      <div className="flex items-start gap-2">
                        <span className="text-muted-foreground min-w-[60px]">镜头:</span>
                        <span className="font-medium">#{description.shotRef}</span>
                      </div>
                      <div className="flex items-start gap-2">
                        <span className="text-muted-foreground min-w-[60px]">尺寸:</span>
                        <span>{description.width} × {description.height}</span>
                      </div>
                      <div className="flex items-start gap-2">
                        <span className="text-muted-foreground min-w-[60px]">提示词:</span>
                        <span className="text-foreground">{description.prompt}</span>
                      </div>
                      {description.negativePrompt && (
                        <div className="flex items-start gap-2">
                          <span className="text-muted-foreground min-w-[60px]">负提示词:</span>
                          <span className="text-foreground">{description.negativePrompt}</span>
                        </div>
                      )}
                    </div>
                  </Card>
                );
              })()}

              <div className="flex justify-center gap-4 mt-4">
                <Badge variant="outline">
                  缩放: {Math.round(zoom * 100)}%
                </Badge>
                {rotation > 0 && (
                  <Badge variant="outline">
                    旋转: {rotation}°
                  </Badge>
                )}
              </div>
            </Card>
          </div>

          <div className="space-y-6">
            <Card className="p-6">
              <h3 className="text-sm font-semibold mb-4 text-muted-foreground">候选信息</h3>
              <div className="space-y-3 text-sm">
                <div>
                  <span className="text-muted-foreground">候选 ID:</span>
                  <span className="ml-2 font-mono">{candidate.id.slice(0, 8)}...</span>
                </div>
                <div>
                  <span className="text-muted-foreground">创建时间:</span>
                  <span className="ml-2">{new Date(candidate.created_at).toLocaleString('zh-CN')}</span>
                </div>
                {candidate.metadata && (
                  <div>
                    <span className="text-muted-foreground">候选索引:</span>
                    <span className="ml-2">#{(candidate.metadata.candidate_index as number) + 1}</span>
                  </div>
                )}
              </div>
            </Card>

            <Card className="p-6">
              <h3 className="text-sm font-semibold mb-4 text-muted-foreground">文件列表</h3>
              <div className="space-y-2 max-h-[40vh] overflow-y-auto">
                {artifacts.length > 0 ? (
                  artifacts.map((artifact, index) => (
                    <div
                      key={artifact.id}
                      className={`flex items-center justify-between p-3 rounded-lg cursor-pointer transition-colors ${
                        index === currentImageIndex
                          ? 'bg-primary/10 border-primary'
                          : 'bg-muted/30 hover:bg-muted/50'
                      }`}
                      onClick={() => setCurrentImageIndex(index)}
                    >
                      <div className="flex items-center gap-3">
                        <Badge variant="outline" className="text-xs">
                          {artifact.file_type}
                        </Badge>
                        <span className="text-sm">{artifact.file_path.split('/').pop()}</span>
                      </div>
                      <Button variant="ghost" size="sm" onClick={() => handleDownload(artifact)}>
                        <Download className="h-4 w-4" />
                      </Button>
                    </div>
                  ))
                ) : (
                  <p className="text-sm text-muted-foreground text-center py-4">暂无文件</p>
                )}
              </div>
            </Card>

            {candidate.content && Object.keys(candidate.content).length > 0 && (
              <Card className="p-6">
                <h3 className="text-sm font-semibold mb-4 text-muted-foreground">内容详情</h3>
                <div className="space-y-2 text-sm max-h-[30vh] overflow-y-auto">
                  {Object.entries(candidate.content).map(([key, value]) => (
                    <div key={key} className="border-b border-border pb-2">
                      <div className="font-medium text-muted-foreground mb-1">
                        {key}
                      </div>
                      <div className="text-foreground">
                        {typeof value === 'string' ? value : JSON.stringify(value, null, 2)}
                      </div>
                    </div>
                  ))}
                </div>
              </Card>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}