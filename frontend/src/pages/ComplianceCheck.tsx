import { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { Plus, Shield, AlertTriangle, CheckCircle, XCircle, FileText, Calendar, Info, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useToast } from "@/hooks/use-toast";
import { useComplianceReports, useCheckCompliance } from "@/hooks/useContinuity";
import { projectApi } from "@/api";
import type { ComplianceCheckRequest } from "@/types/continuity";

export function ComplianceCheck() {
  const { id: projectId } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [dialogOpen, setDialogOpen] = useState(false);
  const [selectedReport, setSelectedReport] = useState<any>(null);
  const [formData, setFormData] = useState<ComplianceCheckRequest>({
    project_id: projectId!,
    check_type: "face_recognition",
    episode_number: undefined,
    stage_type: undefined,
  });

  const { data: project } = useQuery({
    queryKey: ["project", projectId],
    queryFn: () => projectApi.get(projectId!),
    enabled: !!projectId,
  });

  const { data: reports, isLoading, refetch } = useComplianceReports(projectId!);
  const checkMutation = useCheckCompliance();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const result = await checkMutation.mutateAsync(formData);
      toast({ 
        title: "成功", 
        description: `合规检查任务已提交，任务ID: ${result.task_id}` 
      });
      setDialogOpen(false);
      resetForm();
      
      setTimeout(() => {
        refetch();
      }, 2000);
    } catch (error) {
      toast({ 
        title: "错误", 
        description: "检查启动失败",
        variant: "destructive",
      });
    }
  };

  const resetForm = () => {
    setFormData({
      project_id: projectId!,
      check_type: "face_recognition",
      episode_number: undefined,
      stage_type: undefined,
    });
  };

  const handleDialogClose = (open: boolean) => {
    setDialogOpen(open);
    if (!open) {
      resetForm();
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "completed":
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case "failed":
        return <XCircle className="h-5 w-5 text-destructive" />;
      default:
        return <AlertTriangle className="h-5 w-5 text-yellow-500" />;
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case "completed":
        return "已完成";
      case "failed":
        return "失败";
      default:
        return "进行中";
    }
  };

  const getCheckTypeLabel = (type: string) => {
    switch (type) {
      case "face_recognition":
        return "人脸识别";
      case "music_copyright":
        return "音乐版权";
      case "content_moderation":
        return "内容审核";
      default:
        return type;
    }
  };

  const getCheckTypeIcon = (type: string) => {
    switch (type) {
      case "face_recognition":
        return <Shield className="h-4 w-4" />;
      case "music_copyright":
        return <FileText className="h-4 w-4" />;
      case "content_moderation":
        return <AlertTriangle className="h-4 w-4" />;
      default:
        return <Shield className="h-4 w-4" />;
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-muted-foreground">加载中...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start gap-3">
          <Info className="h-4 w-4 text-blue-600 mt-0.5" />
          <div className="flex-1">
            <p className="text-sm text-blue-900">
              <strong>已集成到流水线：</strong>合规检查在每个阶段审核通过后自动执行。
              您可以在这里查看所有合规检查报告，也可以手动启动新的合规检查任务。
            </p>
          </div>
        </div>
      </div>

      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">合规检查</h1>
          <p className="text-muted-foreground mt-1">
            {project?.name || "项目"} - 检查内容合规性和版权问题
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => navigate(`/projects/${projectId}/pipeline`)}>
            <ArrowRight className="mr-2 h-4 w-4" />
            查看流水线
          </Button>
          <Dialog open={dialogOpen} onOpenChange={handleDialogClose}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="mr-2 h-4 w-4" />
                启动检查
              </Button>
            </DialogTrigger>
            <DialogContent>
            <DialogHeader>
              <DialogTitle>启动合规检查</DialogTitle>
              <DialogDescription>
                选择检查类型和范围，开始合规性检查
              </DialogDescription>
            </DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="check_type">检查类型 *</Label>
                <Select
                  value={formData.check_type}
                  onValueChange={(value) => setFormData({ ...formData, check_type: value as any })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="face_recognition">人脸识别</SelectItem>
                    <SelectItem value="music_copyright">音乐版权</SelectItem>
                    <SelectItem value="content_moderation">内容审核</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="episode_number">剧集编号（可选）</Label>
                <Input
                  id="episode_number"
                  type="number"
                  min="1"
                  value={formData.episode_number || ""}
                  onChange={(e) => setFormData({ ...formData, episode_number: e.target.value ? parseInt(e.target.value) : undefined })}
                  placeholder="留空检查所有剧集"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="stage_type">阶段类型（可选）</Label>
                <Input
                  id="stage_type"
                  value={formData.stage_type || ""}
                  onChange={(e) => setFormData({ ...formData, stage_type: e.target.value || undefined })}
                  placeholder="例如：worldbuilding, scriptwriting"
                />
              </div>

              <DialogFooter>
                <Button type="button" variant="outline" onClick={() => setDialogOpen(false)}>
                  取消
                </Button>
                <Button type="submit" disabled={checkMutation.isPending}>
                  {checkMutation.isPending ? "检查中..." : "启动检查"}
                </Button>
              </DialogFooter>
            </form>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {!reports || reports.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <Shield className="h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">暂无合规检查记录</h3>
            <p className="text-muted-foreground text-center mb-4">
              启动合规检查，确保内容符合平台规范和版权要求
            </p>
            <Button onClick={() => setDialogOpen(true)}>
              <Plus className="mr-2 h-4 w-4" />
              启动第一次检查
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {reports.map((report) => (
            <Card key={report.id} className="hover:shadow-md transition-shadow">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      {getCheckTypeIcon(report.check_type)}
                      <CardTitle className="text-lg">{getCheckTypeLabel(report.check_type)}</CardTitle>
                    </div>
                    <CardDescription className="flex items-center gap-2">
                      {getStatusIcon(report.status)}
                      <span>{getStatusLabel(report.status)}</span>
                    </CardDescription>
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => setSelectedReport(report)}
                  >
                    <FileText className="h-4 w-4" />
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-center text-sm">
                  <Calendar className="h-4 w-4 mr-2 text-muted-foreground" />
                  <span className="text-muted-foreground">检查时间:</span>
                  <span className="ml-2">{new Date(report.checked_at).toLocaleString()}</span>
                </div>
                {report.episode_number && (
                  <div className="flex items-center text-sm">
                    <span className="text-muted-foreground mr-2">剧集:</span>
                    <span>第 {report.episode_number} 集</span>
                  </div>
                )}
                {report.stage_type && (
                  <div className="flex items-center text-sm">
                    <span className="text-muted-foreground mr-2">阶段:</span>
                    <span>{report.stage_type}</span>
                  </div>
                )}
                <div className="flex items-center text-sm">
                  <AlertTriangle className={`h-4 w-4 mr-2 ${report.violations > 0 ? "text-destructive" : "text-green-500"}`} />
                  <span className="text-muted-foreground">违规数量:</span>
                  <span className={`ml-2 font-semibold ${report.violations > 0 ? "text-destructive" : "text-green-600"}`}>
                    {report.violations}
                  </span>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {selectedReport && (
        <Dialog open={!!selectedReport} onOpenChange={() => setSelectedReport(null)}>
          <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <div className="flex items-center gap-3">
                {getCheckTypeIcon(selectedReport.check_type)}
                <div>
                  <DialogTitle>{getCheckTypeLabel(selectedReport.check_type)} - 报告详情</DialogTitle>
                  <DialogDescription>
                    {new Date(selectedReport.checked_at).toLocaleString()}
                  </DialogDescription>
                </div>
              </div>
            </DialogHeader>

            <Tabs defaultValue="summary" className="w-full">
              <TabsList className="grid w-full grid-cols-3">
                <TabsTrigger value="summary">概要</TabsTrigger>
                <TabsTrigger value="violations">违规详情</TabsTrigger>
                <TabsTrigger value="details">详细信息</TabsTrigger>
              </TabsList>

              <TabsContent value="summary" className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <Card>
                    <CardHeader className="pb-3">
                      <CardTitle className="text-sm font-medium">检查状态</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="flex items-center gap-2">
                        {getStatusIcon(selectedReport.status)}
                        <span className="text-lg font-semibold">{getStatusLabel(selectedReport.status)}</span>
                      </div>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardHeader className="pb-3">
                      <CardTitle className="text-sm font-medium">违规数量</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className={`text-lg font-semibold ${selectedReport.violations > 0 ? "text-destructive" : "text-green-600"}`}>
                        {selectedReport.violations}
                      </div>
                    </CardContent>
                  </Card>
                </div>

                <div className="space-y-2">
                  <h4 className="font-semibold">检查范围</h4>
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    {selectedReport.episode_number && (
                      <div className="flex items-center">
                        <span className="text-muted-foreground mr-2">剧集:</span>
                        <span>第 {selectedReport.episode_number} 集</span>
                      </div>
                    )}
                    {selectedReport.stage_type && (
                      <div className="flex items-center">
                        <span className="text-muted-foreground mr-2">阶段:</span>
                        <span>{selectedReport.stage_type}</span>
                      </div>
                    )}
                  </div>
                </div>
              </TabsContent>

              <TabsContent value="violations" className="space-y-4">
                {selectedReport.violations === 0 ? (
                  <div className="flex flex-col items-center justify-center py-8">
                    <CheckCircle className="h-12 w-12 text-green-500 mb-4" />
                    <h3 className="text-lg font-semibold mb-2">无违规</h3>
                    <p className="text-muted-foreground text-center">
                      恭喜！本次检查未发现任何违规内容
                    </p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {Object.entries(selectedReport.violations_detail || {}).map(([key, value]: [string, any]) => (
                      <Card key={key} className="border-destructive">
                        <CardHeader className="pb-3">
                          <div className="flex items-center gap-2">
                            <XCircle className="h-5 w-5 text-destructive" />
                            <CardTitle className="text-base">{key}</CardTitle>
                          </div>
                        </CardHeader>
                        <CardContent>
                          <div className="space-y-2 text-sm">
                            {Array.isArray(value) ? (
                              value.map((item: any, index: number) => (
                                <div key={index} className="p-2 bg-destructive/10 rounded">
                                  <div className="font-medium">{item.type || item.title || "违规"}</div>
                                  <div className="text-muted-foreground">{item.message || item.description}</div>
                                </div>
                              ))
                            ) : (
                              <div className="p-2 bg-destructive/10 rounded">
                                <div className="text-muted-foreground">{JSON.stringify(value, null, 2)}</div>
                              </div>
                            )}
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                )}
              </TabsContent>

              <TabsContent value="details" className="space-y-4">
                <div className="space-y-2">
                  <h4 className="font-semibold">原始数据</h4>
                  <pre className="p-4 bg-muted rounded-lg text-xs overflow-x-auto">
                    {JSON.stringify(selectedReport, null, 2)}
                  </pre>
                </div>
              </TabsContent>
            </Tabs>
          </DialogContent>
        </Dialog>
      )}
    </div>
  );
}

export default ComplianceCheck;