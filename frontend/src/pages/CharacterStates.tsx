import { useState } from "react";
import { useParams } from "react-router-dom";
import { useQuery, useMutation } from "@tanstack/react-query";
import { Plus, Edit, Trash2, User, Image as ImageIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/hooks/use-toast";
import { useCharacterStates, useCreateCharacterState, useUpdateCharacterState, useDeleteCharacterState } from "@/hooks/useContinuity";
import { projectApi } from "@/api";
import type { CharacterState, CharacterStateCreate, CharacterStateUpdate } from "@/types/continuity";

export function CharacterStates() {
  const { id: projectId } = useParams<{ id: string }>();
  const { toast } = useToast();
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingState, setEditingState] = useState<CharacterState | null>(null);
  const [formData, setFormData] = useState<Partial<CharacterStateCreate>>({
    character_name: "",
    episode_start: 1,
    episode_end: null,
    outfit_description: "",
    hairstyle: "",
    makeup: "",
    age_appearance: "",
    accessories: {},
    signature_items: {},
    notes: "",
  });

  const { data: project } = useQuery({
    queryKey: ["project", projectId],
    queryFn: () => projectApi.get(projectId!),
    enabled: !!projectId,
  });

  const { data: characterStates, isLoading, refetch } = useCharacterStates(projectId!);
  const createMutation = useCreateCharacterState();
  const updateMutation = useUpdateCharacterState();
  const deleteMutation = useDeleteCharacterState();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingState) {
        await updateMutation.mutateAsync({
          stateId: editingState.id,
          data: formData as CharacterStateUpdate,
        });
        toast({ title: "成功", description: "角色状态已更新" });
      } else {
        await createMutation.mutateAsync({
          ...formData,
          project_id: projectId!,
        } as CharacterStateCreate);
        toast({ title: "成功", description: "角色状态已创建" });
      }
      setDialogOpen(false);
      setEditingState(null);
      resetForm();
      refetch();
    } catch (error) {
      toast({ 
        title: "错误", 
        description: editingState ? "更新失败" : "创建失败",
        variant: "destructive",
      });
    }
  };

  const handleEdit = (state: CharacterState) => {
    setEditingState(state);
    setFormData({
      character_name: state.character_name,
      episode_start: state.episode_start,
      episode_end: state.episode_end,
      outfit_description: state.outfit_description,
      hairstyle: state.hairstyle,
      makeup: state.makeup,
      age_appearance: state.age_appearance,
      accessories: state.accessories,
      signature_items: state.signature_items,
      notes: state.notes,
    });
    setDialogOpen(true);
  };

  const handleDelete = async (stateId: string) => {
    if (confirm("确定要删除这个角色状态吗？")) {
      try {
        await deleteMutation.mutateAsync(stateId);
        toast({ title: "成功", description: "角色状态已删除" });
        refetch();
      } catch (error) {
        toast({ title: "错误", description: "删除失败", variant: "destructive" });
      }
    }
  };

  const resetForm = () => {
    setFormData({
      character_name: "",
      episode_start: 1,
      episode_end: null,
      outfit_description: "",
      hairstyle: "",
      makeup: "",
      age_appearance: "",
      accessories: {},
      signature_items: {},
      notes: "",
    });
  };

  const handleDialogClose = (open: boolean) => {
    setDialogOpen(open);
    if (!open) {
      setEditingState(null);
      resetForm();
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
          <h1 className="text-3xl font-bold">角色状态管理</h1>
          <p className="text-muted-foreground mt-1">
            {project?.name || "项目"} - 管理角色在不同剧集中的外观和状态
          </p>
        </div>
        <Dialog open={dialogOpen} onOpenChange={handleDialogClose}>
          <DialogTrigger asChild>
            <Button onClick={() => setEditingState(null)}>
              <Plus className="mr-2 h-4 w-4" />
              添加角色状态
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>{editingState ? "编辑角色状态" : "添加角色状态"}</DialogTitle>
              <DialogDescription>
                {editingState ? "更新角色的外观和状态信息" : "为角色创建新的状态记录"}
              </DialogDescription>
            </DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="character_name">角色名称 *</Label>
                  <Input
                    id="character_name"
                    value={formData.character_name}
                    onChange={(e) => setFormData({ ...formData, character_name: e.target.value })}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="age_appearance">年龄外观</Label>
                  <Input
                    id="age_appearance"
                    value={formData.age_appearance}
                    onChange={(e) => setFormData({ ...formData, age_appearance: e.target.value })}
                    placeholder="例如：20岁、30岁、中年"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="episode_start">起始剧集 *</Label>
                  <Input
                    id="episode_start"
                    type="number"
                    min="1"
                    value={formData.episode_start}
                    onChange={(e) => setFormData({ ...formData, episode_start: parseInt(e.target.value) })}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="episode_end">结束剧集（可选）</Label>
                  <Input
                    id="episode_end"
                    type="number"
                    min="1"
                    value={formData.episode_end || ""}
                    onChange={(e) => setFormData({ ...formData, episode_end: e.target.value ? parseInt(e.target.value) : null })}
                    placeholder="留空表示持续到最后一集"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="outfit_description">服装描述</Label>
                <Textarea
                  id="outfit_description"
                  value={formData.outfit_description}
                  onChange={(e) => setFormData({ ...formData, outfit_description: e.target.value })}
                  placeholder="描述角色的服装风格、颜色、款式等"
                  rows={3}
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="hairstyle">发型</Label>
                  <Input
                    id="hairstyle"
                    value={formData.hairstyle}
                    onChange={(e) => setFormData({ ...formData, hairstyle: e.target.value })}
                    placeholder="例如：长发、短发、卷发"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="makeup">妆容</Label>
                  <Input
                    id="makeup"
                    value={formData.makeup}
                    onChange={(e) => setFormData({ ...formData, makeup: e.target.value })}
                    placeholder="例如：淡妆、浓妆、无妆"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="notes">备注</Label>
                <Textarea
                  id="notes"
                  value={formData.notes}
                  onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                  placeholder="其他需要注意的细节"
                  rows={2}
                />
              </div>

              <DialogFooter>
                <Button type="button" variant="outline" onClick={() => setDialogOpen(false)}>
                  取消
                </Button>
                <Button type="submit" disabled={createMutation.isPending || updateMutation.isPending}>
                  {createMutation.isPending || updateMutation.isPending ? "保存中..." : editingState ? "更新" : "创建"}
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {!characterStates || characterStates.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <User className="h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">暂无角色状态</h3>
            <p className="text-muted-foreground text-center mb-4">
              开始添加角色状态，确保角色在不同剧集中的外观一致性
            </p>
            <Button onClick={() => setDialogOpen(true)}>
              <Plus className="mr-2 h-4 w-4" />
              添加第一个角色状态
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {characterStates.map((state) => (
            <Card key={state.id} className="hover:shadow-md transition-shadow">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <CardTitle className="text-lg">{state.character_name}</CardTitle>
                    <CardDescription className="mt-1">
                      第 {state.episode_start} 集
                      {state.episode_end && ` - 第 ${state.episode_end} 集`}
                      {!state.episode_end && " - 持续"}
                    </CardDescription>
                  </div>
                  <div className="flex gap-1">
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => handleEdit(state)}
                    >
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => handleDelete(state.id)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-3">
                {state.age_appearance && (
                  <div className="flex items-center text-sm">
                    <User className="h-4 w-4 mr-2 text-muted-foreground" />
                    <span className="text-muted-foreground">年龄:</span>
                    <span className="ml-2">{state.age_appearance}</span>
                  </div>
                )}
                {state.outfit_description && (
                  <div className="flex items-start text-sm">
                    <ImageIcon className="h-4 w-4 mr-2 text-muted-foreground mt-0.5" />
                    <div className="flex-1">
                      <span className="text-muted-foreground">服装:</span>
                      <p className="mt-1 line-clamp-2">{state.outfit_description}</p>
                    </div>
                  </div>
                )}
                {state.hairstyle && (
                  <div className="flex items-center text-sm">
                    <span className="text-muted-foreground mr-2">发型:</span>
                    <span>{state.hairstyle}</span>
                  </div>
                )}
                {state.makeup && (
                  <div className="flex items-center text-sm">
                    <span className="text-muted-foreground mr-2">妆容:</span>
                    <span>{state.makeup}</span>
                  </div>
                )}
                {state.signature_items && Object.keys(state.signature_items).length > 0 && (
                  <div className="flex flex-wrap gap-1 mt-2">
                    {Object.entries(state.signature_items).map(([key, value]) => (
                      <Badge key={key} variant="secondary" className="text-xs">
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

export default CharacterStates;