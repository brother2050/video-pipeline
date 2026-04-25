/**
 * 项目列表页
 * - 卡片网格展示所有项目
 * - 新建项目对话框
 * - 分页
 */

import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useProjects, useCreateProject, useDeleteProject } from "@/hooks/useProjects";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { EmptyState } from "@/components/shared/EmptyState";
import { ConfirmDialog } from "@/components/shared/ConfirmDialog";
import { formatDate } from "@/lib/utils";
import { STAGE_LABELS } from "@/lib/constants";
import { Plus, Trash2 } from "lucide-react";
import { StageStatus } from "@/types";
import type { ProjectCreate } from "@/types";

export default function ProjectList() {
  const navigate = useNavigate();
  const [page, setPage] = useState(1);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [deleteId, setDeleteId] = useState<string | null>(null);
  const [form, setForm] = useState<ProjectCreate>({
    name: "", description: "", genre: "",
    target_episodes: 1, target_duration_minutes: 30,
  });

  const { data, isLoading } = useProjects(page, 12);
  const createMut = useCreateProject();
  const deleteMut = useDeleteProject();

  const handleCreate = async () => {
    await createMut.mutateAsync(form);
    setDialogOpen(false);
    setForm({ name: "", description: "", genre: "", target_episodes: 1, target_duration_minutes: 30 });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">项目管理</h1>
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button><Plus className="h-4 w-4 mr-2" />新建项目</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>新建项目</DialogTitle>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <Label>项目名称</Label>
                <Input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="我的影视项目" />
              </div>
              <div>
                <Label>描述</Label>
                <Textarea value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} placeholder="项目简介..." rows={3} />
              </div>
              <div>
                <Label>题材类型</Label>
                <Input value={form.genre} onChange={(e) => setForm({ ...form, genre: e.target.value })} placeholder="科幻、悬疑、都市..." />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>目标集数</Label>
                  <Input type="number" min={1} value={form.target_episodes} onChange={(e) => setForm({ ...form, target_episodes: parseInt(e.target.value) || 1 })} />
                </div>
                <div>
                  <Label>每集时长(分钟)</Label>
                  <Input type="number" min={1} value={form.target_duration_minutes} onChange={(e) => setForm({ ...form, target_duration_minutes: parseInt(e.target.value) || 30 })} />
                </div>
              </div>
              <Button className="w-full" onClick={handleCreate} disabled={!form.name || createMut.isPending}>
                {createMut.isPending ? "创建中..." : "创建项目"}
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {isLoading ? (
        <div className="text-center py-12 text-muted-foreground">加载中...</div>
      ) : data && data.items.length > 0 ? (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {data.items.map((p) => {
              const completedCount = p.stages_summary.filter(s => s.status === StageStatus.LOCKED).length;
              return (
                <Card key={p.id} className="p-4 hover:bg-accent/30 transition-colors">
                  <div className="cursor-pointer" onClick={() => navigate(`/projects/${p.id}/pipeline`)}>
                    <div className="flex items-start justify-between mb-2">
                      <h3 className="font-medium">{p.name}</h3>
                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-6 w-6 p-0 text-muted-foreground hover:text-destructive"
                        onClick={(e) => { e.stopPropagation(); setDeleteId(p.id); }}
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                      </Button>
                    </div>
                    <p className="text-sm text-muted-foreground line-clamp-2 mb-3">{p.description || "无描述"}</p>
                    {p.genre && <span className="text-xs bg-secondary px-2 py-0.5 rounded">{p.genre}</span>}
                    <div className="mt-3">
                      <div className="flex items-center justify-between text-xs text-muted-foreground mb-1">
                        <span>进度</span>
                        <span>{completedCount}/9</span>
                      </div>
                      <div className="h-1.5 bg-secondary rounded-full overflow-hidden">
                        <div className="h-full bg-primary rounded-full transition-all" style={{ width: `${(completedCount / 9) * 100}%` }} />
                      </div>
                    </div>
                    <div className="mt-2 flex items-center justify-between">
                      <span className="text-xs text-muted-foreground">{STAGE_LABELS[p.current_stage]}</span>
                      <span className="text-xs text-muted-foreground">{formatDate(p.updated_at)}</span>
                    </div>
                  </div>
                </Card>
              );
            })}
          </div>
          {data.total > 12 && (
            <div className="flex justify-center gap-2">
              <Button variant="outline" size="sm" disabled={page <= 1} onClick={() => setPage(page - 1)}>上一页</Button>
              <span className="text-sm text-muted-foreground py-1">第 {page} 页 / 共 {Math.ceil(data.total / 12)} 页</span>
              <Button variant="outline" size="sm" disabled={page >= Math.ceil(data.total / 12)} onClick={() => setPage(page + 1)}>下一页</Button>
            </div>
          )}
        </>
      ) : (
        <EmptyState title="暂无项目" description="点击新建项目开始创作" action={
          <Button onClick={() => setDialogOpen(true)}><Plus className="h-4 w-4 mr-2" />新建项目</Button>
        } />
      )}

      <ConfirmDialog
        open={!!deleteId}
        onOpenChange={() => setDeleteId(null)}
        title="删除项目"
        description="此操作不可恢复，项目的所有阶段数据和素材文件将被永久删除。"
        destructive
        onConfirm={async () => {
          if (deleteId) {
            await deleteMut.mutateAsync(deleteId);
            setDeleteId(null);
          }
        }}
      />
    </div>
  );
}
