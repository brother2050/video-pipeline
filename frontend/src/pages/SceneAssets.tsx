import { useState } from "react";
import { useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { Plus, Edit, Trash2, Home, Building2, Image as ImageIcon, MapPin } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/hooks/use-toast";
import { useSceneAssets, useCreateSceneAsset, useUpdateSceneAsset, useDeleteSceneAsset } from "@/hooks/useContinuity";
import { projectApi } from "@/api";
import type { SceneAsset, SceneAssetCreate, SceneAssetUpdate } from "@/types/continuity";

export function SceneAssets() {
  const { id: projectId } = useParams<{ id: string }>();
  const { toast } = useToast();
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingAsset, setEditingAsset] = useState<SceneAsset | null>(null);
  const [formData, setFormData] = useState<Partial<SceneAssetCreate>>({
    scene_name: "",
    scene_type: "interior",
    description: "",
    layout_description: "",
    lora_path: "",
    controlnet_depth_path: "",
    controlnet_edge_path: "",
    reference_image_path: "",
    variants: {},
  });

  const { data: project } = useQuery({
    queryKey: ["project", projectId],
    queryFn: () => projectApi.get(projectId!),
    enabled: !!projectId,
  });

  const { data: sceneAssets, isLoading, refetch } = useSceneAssets(projectId!);
  const createMutation = useCreateSceneAsset();
  const updateMutation = useUpdateSceneAsset();
  const deleteMutation = useDeleteSceneAsset();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingAsset) {
        await updateMutation.mutateAsync({
          assetId: editingAsset.id,
          data: formData as SceneAssetUpdate,
        });
        toast({ title: "成功", description: "场景资产已更新" });
      } else {
        await createMutation.mutateAsync({
          ...formData,
          project_id: projectId!,
        } as SceneAssetCreate);
        toast({ title: "成功", description: "场景资产已创建" });
      }
      setDialogOpen(false);
      setEditingAsset(null);
      resetForm();
      refetch();
    } catch (error) {
      toast({ 
        title: "错误", 
        description: editingAsset ? "更新失败" : "创建失败",
        variant: "destructive",
      });
    }
  };

  const handleEdit = (asset: SceneAsset) => {
    setEditingAsset(asset);
    setFormData({
      scene_name: asset.scene_name,
      scene_type: asset.scene_type,
      description: asset.description,
      layout_description: asset.layout_description,
      lora_path: asset.lora_path || "",
      controlnet_depth_path: asset.controlnet_depth_path || "",
      controlnet_edge_path: asset.controlnet_edge_path || "",
      reference_image_path: asset.reference_image_path || "",
      variants: asset.variants,
    });
    setDialogOpen(true);
  };

  const handleDelete = async (assetId: string) => {
    if (confirm("确定要删除这个场景资产吗？")) {
      try {
        await deleteMutation.mutateAsync(assetId);
        toast({ title: "成功", description: "场景资产已删除" });
        refetch();
      } catch (error) {
        toast({ title: "错误", description: "删除失败", variant: "destructive" });
      }
    }
  };

  const resetForm = () => {
    setFormData({
      scene_name: "",
      scene_type: "interior",
      description: "",
      layout_description: "",
      lora_path: "",
      controlnet_depth_path: "",
      controlnet_edge_path: "",
      reference_image_path: "",
      variants: {},
    });
  };

  const handleDialogClose = (open: boolean) => {
    setDialogOpen(open);
    if (!open) {
      setEditingAsset(null);
      resetForm();
    }
  };

  const getSceneTypeIcon = (type: string) => {
    switch (type) {
      case "interior":
        return <Home className="h-4 w-4" />;
      case "exterior":
        return <MapPin className="h-4 w-4" />;
      default:
        return <Building2 className="h-4 w-4" />;
    }
  };

  const getSceneTypeLabel = (type: string) => {
    switch (type) {
      case "interior":
        return "室内";
      case "exterior":
        return "室外";
      default:
        return "混合";
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
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">场景资产管理</h1>
          <p className="text-muted-foreground mt-1">
            {project?.name || "项目"} - 管理可重复使用的场景资产
          </p>
        </div>
        <Dialog open={dialogOpen} onOpenChange={handleDialogClose}>
          <DialogTrigger asChild>
            <Button onClick={() => setEditingAsset(null)}>
              <Plus className="mr-2 h-4 w-4" />
              添加场景资产
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>{editingAsset ? "编辑场景资产" : "添加场景资产"}</DialogTitle>
              <DialogDescription>
                {editingAsset ? "更新场景资产信息" : "创建新的场景资产，用于多集制作"}
              </DialogDescription>
            </DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="scene_name">场景名称 *</Label>
                  <Input
                    id="scene_name"
                    value={formData.scene_name}
                    onChange={(e) => setFormData({ ...formData, scene_name: e.target.value })}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="scene_type">场景类型 *</Label>
                  <Select
                    value={formData.scene_type}
                    onValueChange={(value) => setFormData({ ...formData, scene_type: value as any })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="interior">室内</SelectItem>
                      <SelectItem value="exterior">室外</SelectItem>
                      <SelectItem value="mixed">混合</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="description">场景描述</Label>
                <Textarea
                  id="description"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="描述场景的整体风格、氛围、时间等"
                  rows={3}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="layout_description">布局描述</Label>
                <Textarea
                  id="layout_description"
                  value={formData.layout_description}
                  onChange={(e) => setFormData({ ...formData, layout_description: e.target.value })}
                  placeholder="描述场景的布局、家具摆放、空间结构等"
                  rows={3}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="lora_path">LoRA 路径</Label>
                <Input
                  id="lora_path"
                  value={formData.lora_path || ""}
                  onChange={(e) => setFormData({ ...formData, lora_path: e.target.value })}
                  placeholder="场景风格 LoRA 模型路径"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="controlnet_depth_path">ControlNet 深度路径</Label>
                  <Input
                    id="controlnet_depth_path"
                    value={formData.controlnet_depth_path || ""}
                    onChange={(e) => setFormData({ ...formData, controlnet_depth_path: e.target.value })}
                    placeholder="深度图路径"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="controlnet_edge_path">ControlNet 边缘路径</Label>
                  <Input
                    id="controlnet_edge_path"
                    value={formData.controlnet_edge_path || ""}
                    onChange={(e) => setFormData({ ...formData, controlnet_edge_path: e.target.value })}
                    placeholder="边缘图路径"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="reference_image_path">参考图片路径</Label>
                <Input
                  id="reference_image_path"
                  value={formData.reference_image_path || ""}
                  onChange={(e) => setFormData({ ...formData, reference_image_path: e.target.value })}
                  placeholder="场景参考图片路径"
                />
              </div>

              <DialogFooter>
                <Button type="button" variant="outline" onClick={() => setDialogOpen(false)}>
                  取消
                </Button>
                <Button type="submit" disabled={createMutation.isPending || updateMutation.isPending}>
                  {createMutation.isPending || updateMutation.isPending ? "保存中..." : editingAsset ? "更新" : "创建"}
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {!sceneAssets || sceneAssets.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <Building2 className="h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">暂无场景资产</h3>
            <p className="text-muted-foreground text-center mb-4">
              开始添加场景资产，确保场景在不同剧集中的视觉一致性
            </p>
            <Button onClick={() => setDialogOpen(true)}>
              <Plus className="mr-2 h-4 w-4" />
              添加第一个场景资产
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {sceneAssets.map((asset) => (
            <Card key={asset.id} className="hover:shadow-md transition-shadow">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      {getSceneTypeIcon(asset.scene_type)}
                      <CardTitle className="text-lg">{asset.scene_name}</CardTitle>
                    </div>
                    <CardDescription className="flex items-center gap-2">
                      <Badge variant="secondary">{getSceneTypeLabel(asset.scene_type)}</Badge>
                    </CardDescription>
                  </div>
                  <div className="flex gap-1">
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => handleEdit(asset)}
                    >
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => handleDelete(asset.id)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-3">
                {asset.description && (
                  <div className="flex items-start text-sm">
                    <ImageIcon className="h-4 w-4 mr-2 text-muted-foreground mt-0.5" />
                    <div className="flex-1">
                      <p className="line-clamp-2">{asset.description}</p>
                    </div>
                  </div>
                )}
                {asset.layout_description && (
                  <div className="flex items-start text-sm">
                    <MapPin className="h-4 w-4 mr-2 text-muted-foreground mt-0.5" />
                    <div className="flex-1">
                      <span className="text-muted-foreground">布局:</span>
                      <p className="mt-1 line-clamp-2">{asset.layout_description}</p>
                    </div>
                  </div>
                )}
                {asset.lora_path && (
                  <div className="flex items-center text-sm">
                    <span className="text-muted-foreground mr-2">LoRA:</span>
                    <span className="line-clamp-1 text-xs">{asset.lora_path}</span>
                  </div>
                )}
                {asset.variants && Object.keys(asset.variants).length > 0 && (
                  <div className="flex flex-wrap gap-1 mt-2">
                    {Object.keys(asset.variants).map((key) => (
                      <Badge key={key} variant="outline" className="text-xs">
                        {key}
                      </Badge>
                    ))}
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

export default SceneAssets;