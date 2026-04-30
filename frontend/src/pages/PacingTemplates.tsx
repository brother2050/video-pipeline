import { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { Plus, Edit, Trash2, Clock, PlayCircle, CheckCircle, XCircle, AlertCircle, Info, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useToast } from "@/hooks/use-toast";
import { usePacingTemplates, useCreatePacingTemplate, useUpdatePacingTemplate, useDeletePacingTemplate, useValidatePacing } from "@/hooks/useContinuity";
import { projectApi } from "@/api";
import type { PacingTemplate, PacingTemplateCreate, PacingValidationRequest, PacingValidationResult } from "@/types/continuity";

export function PacingTemplates() {
  const { id: projectId } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState<PacingTemplate | null>(null);
  const [validateDialogOpen, setValidateDialogOpen] = useState(false);
  const [validationResult, setValidationResult] = useState<PacingValidationResult | null>(null);
  const [formData, setFormData] = useState<Partial<PacingTemplateCreate>>({
    name: "",
    description: "",
    genre: "",
    structure: {},
    hook_3sec_config: {},
    cliffhanger_config: {},
    target_duration_sec: 60,
  });
  const [validateFormData, setValidateFormData] = useState<PacingValidationRequest>({
    scene_content: {},
    template_id: "",
    hook_config: {},
  });

  const { data: templates, isLoading, refetch } = usePacingTemplates();
  const { data: project } = useQuery({
    queryKey: ["project", projectId],
    queryFn: () => projectApi.get(projectId!),
    enabled: !!projectId,
  });
  const createMutation = useCreatePacingTemplate();
  const updateMutation = useUpdatePacingTemplate();
  const deleteMutation = useDeletePacingTemplate();
  const validateMutation = useValidatePacing();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingTemplate) {
        await updateMutation.mutateAsync({
          templateId: editingTemplate.id,
          data: formData as Partial<PacingTemplateCreate>,
        });
        toast({ title: "成功", description: "节奏模板已更新" });
      } else {
        await createMutation.mutateAsync(formData as PacingTemplateCreate);
        toast({ title: "成功", description: "节奏模板已创建" });
      }
      setDialogOpen(false);
      setEditingTemplate(null);
      resetForm();
      refetch();
    } catch {
      toast({ 
        title: "错误", 
        description: editingTemplate ? "更新失败" : "创建失败",
        variant: "destructive",
      });
    }
  };

  const handleValidate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const result = await validateMutation.mutateAsync(validateFormData);
      setValidationResult(result);
      toast({ title: "验证完成", description: "节奏验证已完成" });
    } catch {
      toast({ title: "错误", description: "验证失败", variant: "destructive" });
    }
  };

  const handleEdit = (template: PacingTemplate) => {
    setEditingTemplate(template);
    setFormData({
      name: template.name,
      description: template.description,
      genre: template.genre,
      structure: template.structure,
      hook_3sec_config: template.hook_3sec_config,
      cliffhanger_config: template.cliffhanger_config,
      target_duration_sec: template.target_duration_sec,
    });
    setDialogOpen(true);
  };

  const handleDelete = async (templateId: string) => {
    if (confirm("确定要删除这个节奏模板吗？")) {
      try {
        await deleteMutation.mutateAsync(templateId);
        toast({ title: "成功", description: "节奏模板已删除" });
        refetch();
      } catch {
        toast({ title: "错误", description: "删除失败", variant: "destructive" });
      }
    }
  };

  const resetForm = () => {
    setFormData({
      name: "",
      description: "",
      genre: "",
      structure: {},
      hook_3sec_config: {},
      cliffhanger_config: {},
      target_duration_sec: 60,
    });
  };

  const handleDialogClose = (open: boolean) => {
    setDialogOpen(open);
    if (!open) {
      setEditingTemplate(null);
      resetForm();
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case "error":
        return <XCircle className="h-4 w-4 text-destructive" />;
      case "warning":
        return <AlertCircle className="h-4 w-4 text-yellow-500" />;
      default:
        return <CheckCircle className="h-4 w-4 text-green-500" />;
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
              <strong>已集成到流水线：</strong>节奏模板在"剧情大纲"阶段审核通过后自动提取并保存。
              您可以在这里查看和编辑节奏模板，也可以手动添加新的节奏模板记录。
            </p>
          </div>
        </div>
      </div>

      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">节奏模板管理</h1>
          <p className="text-muted-foreground mt-1">
            {project?.name || "项目"} - 管理和验证短剧节奏模板
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => navigate(`/projects/${projectId}/pipeline`)}>
            <ArrowRight className="mr-2 h-4 w-4" />
            查看流水线
          </Button>
          <Dialog open={validateDialogOpen} onOpenChange={setValidateDialogOpen}>
            <DialogTrigger asChild>
              <Button variant="outline">
                <PlayCircle className="mr-2 h-4 w-4" />
                验证节奏
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle>验证节奏</DialogTitle>
                <DialogDescription>
                  使用节奏模板验证场景内容的节奏是否符合要求
                </DialogDescription>
              </DialogHeader>
              <form onSubmit={handleValidate} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="template_id">选择模板（可选）</Label>
                  <Select
                    value={validateFormData.template_id}
                    onValueChange={(value) => setValidateFormData({ ...validateFormData, template_id: value })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="选择节奏模板" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="">不使用模板</SelectItem>
                      {templates?.map((template) => (
                        <SelectItem key={template.id} value={template.id}>
                          {template.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="scene_content">场景内容（JSON）</Label>
                  <Textarea
                    id="scene_content"
                    value={JSON.stringify(validateFormData.scene_content, null, 2)}
                    onChange={(e) => {
                      try {
                        setValidateFormData({ ...validateFormData, scene_content: JSON.parse(e.target.value) });
                      } catch {
                        setValidateFormData({ ...validateFormData, scene_content: {} });
                      }
                    }}
                    placeholder='{"action": "...", "dialogue": ["..."]}'
                    rows={8}
                    className="font-mono text-xs"
                  />
                </div>

                <DialogFooter>
                  <Button type="button" variant="outline" onClick={() => setValidateDialogOpen(false)}>
                    取消
                  </Button>
                  <Button type="submit" disabled={validateMutation.isPending}>
                    {validateMutation.isPending ? "验证中..." : "验证"}
                  </Button>
                </DialogFooter>
              </form>

              {validationResult && (
                <div className="mt-4 p-4 border rounded-lg">
                  <h4 className="font-semibold mb-3">验证结果</h4>
                  {validationResult.valid ? (
                    <div className="flex items-center gap-2 text-green-600">
                      <CheckCircle className="h-5 w-5" />
                      <span>节奏验证通过</span>
                    </div>
                  ) : (
                    <div className="space-y-2">
                      {validationResult.issues.map((issue, index) => (
                        <div key={index} className="flex items-start gap-2 p-2 bg-muted rounded">
                          {getSeverityIcon(issue.severity)}
                          <div className="flex-1">
                            <div className="font-medium">{issue.type}</div>
                            <div className="text-sm text-muted-foreground">{issue.message}</div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </DialogContent>
          </Dialog>

          <Dialog open={dialogOpen} onOpenChange={handleDialogClose}>
            <DialogTrigger asChild>
              <Button onClick={() => setEditingTemplate(null)}>
                <Plus className="mr-2 h-4 w-4" />
                添加模板
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
              <DialogHeader>
                <DialogTitle>{editingTemplate ? "编辑节奏模板" : "添加节奏模板"}</DialogTitle>
                <DialogDescription>
                  {editingTemplate ? "更新节奏模板配置" : "创建新的节奏模板"}
                </DialogDescription>
              </DialogHeader>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="name">模板名称 *</Label>
                    <Input
                      id="name"
                      value={formData.name}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="genre">类型</Label>
                    <Input
                      id="genre"
                      value={formData.genre}
                      onChange={(e) => setFormData({ ...formData, genre: e.target.value })}
                      placeholder="例如：drama, romance, mystery"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="description">描述</Label>
                  <Textarea
                    id="description"
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    placeholder="描述这个节奏模板的特点"
                    rows={2}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="target_duration_sec">目标时长（秒）</Label>
                  <Input
                    id="target_duration_sec"
                    type="number"
                    min="1"
                    value={formData.target_duration_sec}
                    onChange={(e) => setFormData({ ...formData, target_duration_sec: parseInt(e.target.value) })}
                  />
                </div>

                <Tabs defaultValue="structure" className="w-full">
                  <TabsList className="grid w-full grid-cols-3">
                    <TabsTrigger value="structure">结构</TabsTrigger>
                    <TabsTrigger value="hook">3秒钩子</TabsTrigger>
                    <TabsTrigger value="cliffhanger">悬念结尾</TabsTrigger>
                  </TabsList>
                  
                  <TabsContent value="structure" className="space-y-2">
                    <Label htmlFor="structure">结构配置（JSON）</Label>
                    <Textarea
                      id="structure"
                      value={JSON.stringify(formData.structure, null, 2)}
                      onChange={(e) => {
                        try {
                          setFormData({ ...formData, structure: JSON.parse(e.target.value) });
                        } catch {
                          setFormData({ ...formData, structure: {} });
                        }
                      }}
                      placeholder='{"sections": [{"type": "setup", "duration_sec": 15}]}'
                      rows={8}
                      className="font-mono text-xs"
                    />
                  </TabsContent>

                  <TabsContent value="hook" className="space-y-2">
                    <Label htmlFor="hook_3sec_config">3秒钩子配置（JSON）</Label>
                    <Textarea
                      id="hook_3sec_config"
                      value={JSON.stringify(formData.hook_3sec_config, null, 2)}
                      onChange={(e) => {
                        try {
                          setFormData({ ...formData, hook_3sec_config: JSON.parse(e.target.value) });
                        } catch {
                          setFormData({ ...formData, hook_3sec_config: {} });
                        }
                      }}
                      placeholder='{"conflict_keywords": ["冲突", "争吵"]}'
                      rows={8}
                      className="font-mono text-xs"
                    />
                  </TabsContent>

                  <TabsContent value="cliffhanger" className="space-y-2">
                    <Label htmlFor="cliffhanger_config">悬念结尾配置（JSON）</Label>
                    <Textarea
                      id="cliffhanger_config"
                      value={JSON.stringify(formData.cliffhanger_config, null, 2)}
                      onChange={(e) => {
                        try {
                          setFormData({ ...formData, cliffhanger_config: JSON.parse(e.target.value) });
                        } catch {
                          setFormData({ ...formData, cliffhanger_config: {} });
                        }
                      }}
                      placeholder='{"cliffhanger_keywords": ["突然", "意外"]}'
                      rows={8}
                      className="font-mono text-xs"
                    />
                  </TabsContent>
                </Tabs>

                <DialogFooter>
                  <Button type="button" variant="outline" onClick={() => setDialogOpen(false)}>
                    取消
                  </Button>
                  <Button type="submit" disabled={createMutation.isPending || updateMutation.isPending}>
                    {createMutation.isPending || updateMutation.isPending ? "保存中..." : editingTemplate ? "更新" : "创建"}
                  </Button>
                </DialogFooter>
              </form>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {!templates || templates.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <Clock className="h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">暂无节奏模板</h3>
            <p className="text-muted-foreground text-center mb-4">
              开始添加节奏模板，用于短剧节奏控制和验证
            </p>
            <Button onClick={() => setDialogOpen(true)}>
              <Plus className="mr-2 h-4 w-4" />
              添加第一个节奏模板
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {templates.map((template) => (
            <Card key={template.id} className="hover:shadow-md transition-shadow">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <CardTitle className="text-lg">{template.name}</CardTitle>
                    <CardDescription className="mt-1">
                      {template.description || "无描述"}
                    </CardDescription>
                  </div>
                  <div className="flex gap-1">
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => handleEdit(template)}
                    >
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => handleDelete(template.id)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-3">
                {template.genre && (
                  <Badge variant="secondary">{template.genre}</Badge>
                )}
                <div className="flex items-center text-sm">
                  <Clock className="h-4 w-4 mr-2 text-muted-foreground" />
                  <span className="text-muted-foreground">目标时长:</span>
                  <span className="ml-2">{template.target_duration_sec} 秒</span>
                </div>
                <div className="flex items-center text-sm">
                  <PlayCircle className="h-4 w-4 mr-2 text-muted-foreground" />
                  <span className="text-muted-foreground">使用次数:</span>
                  <span className="ml-2">{template.usage_count}</span>
                </div>
                {template.avg_completion_rate > 0 && (
                  <div className="flex items-center text-sm">
                    <CheckCircle className="h-4 w-4 mr-2 text-muted-foreground" />
                    <span className="text-muted-foreground">完成率:</span>
                    <span className="ml-2">{(template.avg_completion_rate * 100).toFixed(1)}%</span>
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}

export default PacingTemplates;