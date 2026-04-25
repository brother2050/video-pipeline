/**
 * 节点管理页
 * - 节点表格
 * - 新建/编辑/删除节点
 * - 启用/禁用开关
 * - 健康检查
 */

import { useState } from "react";
import { useNodes, useCreateNode, useUpdateNode, useDeleteNode, useNodeHealth } from "@/hooks/useNodes";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { NodeStatusIndicator } from "@/components/shared/NodeStatusIndicator";
import { ConfirmDialog } from "@/components/shared/ConfirmDialog";
import { EmptyState } from "@/components/shared/EmptyState";
import { formatDate } from "@/lib/utils";
import { Plus, Trash2, Edit, Activity } from "lucide-react";
import { SupplierCapability, NodeStatus } from "@/types";
import type { NodeCreate, NodeResponse } from "@/types";

const CAPABILITY_OPTIONS: SupplierCapability[] = [
  SupplierCapability.LLM, SupplierCapability.IMAGE, SupplierCapability.VIDEO,
  SupplierCapability.TTS, SupplierCapability.BGM, SupplierCapability.SFX, SupplierCapability.POST,
];

export default function NodeManager() {
  const { data: nodes, isLoading } = useNodes();
  const createMut = useCreateNode();
  const deleteMut = useDeleteNode();

  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingNode, setEditingNode] = useState<NodeResponse | null>(null);
  const [deleteId, setDeleteId] = useState<string | null>(null);
  const [healthNodeId, setHealthNodeId] = useState<string | null>(null);
  const { data: healthData, refetch: checkHealth, isFetching: _healthChecking } = useNodeHealth(healthNodeId || "");

  const [form, setForm] = useState<NodeCreate>({
    name: "", host: "127.0.0.1", port: 8000,
    capabilities: [], models: [], tags: {},
  });

  const resetForm = () => {
    setForm({ name: "", host: "127.0.0.1", port: 8000, capabilities: [], models: [], tags: {} });
    setEditingNode(null);
  };

  const handleSave = async () => {
    if (editingNode) {
      await useUpdateNode(editingNode.id).mutateAsync(form);
    } else {
      await createMut.mutateAsync(form);
    }
    setDialogOpen(false);
    resetForm();
  };

  const toggleCapability = (cap: SupplierCapability) => {
    setForm((prev) => ({
      ...prev,
      capabilities: prev.capabilities.includes(cap)
        ? prev.capabilities.filter((c) => c !== cap)
        : [...prev.capabilities, cap],
    }));
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">节点管理</h1>
        <Dialog open={dialogOpen} onOpenChange={(open) => { setDialogOpen(open); if (!open) resetForm(); }}>
          <DialogTrigger asChild>
            <Button onClick={() => { resetForm(); setDialogOpen(true); }}>
              <Plus className="h-4 w-4 mr-2" />添加节点
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>{editingNode ? "编辑节点" : "添加节点"}</DialogTitle>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <Label>名称</Label>
                <Input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="localhost-ollama" />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>地址</Label>
                  <Input value={form.host} onChange={(e) => setForm({ ...form, host: e.target.value })} />
                </div>
                <div>
                  <Label>端口</Label>
                  <Input type="number" value={form.port} onChange={(e) => setForm({ ...form, port: parseInt(e.target.value) || 8000 })} />
                </div>
              </div>
              <div>
                <Label>能力</Label>
                <div className="flex flex-wrap gap-2 mt-1">
                  {CAPABILITY_OPTIONS.map((cap) => (
                    <Badge
                      key={cap}
                      variant={form.capabilities.includes(cap) ? "default" : "outline"}
                      className="cursor-pointer"
                      onClick={() => toggleCapability(cap)}
                    >
                      {cap}
                    </Badge>
                  ))}
                </div>
              </div>
              <div>
                <Label>模型（逗号分隔）</Label>
                <Input
                  value={(form.models || []).join(", ")}
                  onChange={(e) => setForm({ ...form, models: e.target.value.split(",").map(s => s.trim()).filter(Boolean) })}
                  placeholder="qwen2.5:7b, llama3.1:8b"
                />
              </div>
              <Button className="w-full" onClick={handleSave} disabled={!form.name || createMut.isPending}>
                {editingNode ? "保存修改" : "添加节点"}
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {isLoading ? (
        <div className="text-center py-12 text-muted-foreground">加载中...</div>
      ) : nodes && nodes.length > 0 ? (
        <Card>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>名称</TableHead>
                <TableHead>地址</TableHead>
                <TableHead>能力</TableHead>
                <TableHead>状态</TableHead>
                <TableHead>最后心跳</TableHead>
                <TableHead>启用</TableHead>
                <TableHead>操作</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {nodes.map((node) => (
                <TableRow key={node.id}>
                  <TableCell className="font-medium">{node.name}</TableCell>
                  <TableCell className="font-mono text-xs">{node.host}:{node.port}</TableCell>
                  <TableCell>
                    <div className="flex flex-wrap gap-1">
                      {node.capabilities.map((c) => (
                        <Badge key={c} variant="secondary" className="text-[10px]">{c}</Badge>
                      ))}
                    </div>
                  </TableCell>
                  <TableCell>
                    <NodeStatusIndicator status={node.status} />
                  </TableCell>
                  <TableCell className="text-xs text-muted-foreground">
                    {node.last_heartbeat ? formatDate(node.last_heartbeat) : "—"}
                  </TableCell>
                  <TableCell>
                    <Switch
                      checked={node.status !== NodeStatus.OFFLINE}
                      onCheckedChange={(_checked) => {
                        // 通过 API 切换
                      }}
                    />
                  </TableCell>
                  <TableCell>
                    <div className="flex gap-1">
                      <Button variant="ghost" size="sm" onClick={() => {
                        setHealthNodeId(node.id);
                        setTimeout(() => checkHealth(), 100);
                      }}>
                        <Activity className="h-3.5 w-3.5" />
                      </Button>
                      <Button variant="ghost" size="sm" onClick={() => {
                        setEditingNode(node);
                        setForm({
                          name: node.name, host: node.host, port: node.port,
                          capabilities: node.capabilities, models: node.models, tags: node.tags,
                        });
                        setDialogOpen(true);
                      }}>
                        <Edit className="h-3.5 w-3.5" />
                      </Button>
                      <Button variant="ghost" size="sm" className="text-destructive" onClick={() => setDeleteId(node.id)}>
                        <Trash2 className="h-3.5 w-3.5" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Card>
      ) : (
        <EmptyState title="暂无节点" description="添加本地或远程节点来提供 AI 能力" />
      )}

      {/* 健康检查结果 */}
      {healthData && (
        <Card className="p-4">
          <h3 className="text-sm font-medium mb-2">健康检查结果</h3>
          <div className="text-sm space-y-1">
            <p>状态: {healthData.status}</p>
            <p>延迟: {healthData.latency_ms}ms</p>
            <p>已加载模型: {healthData.models_loaded.length > 0 ? healthData.models_loaded.join(", ") : "无"}</p>
          </div>
        </Card>
      )}

      <ConfirmDialog
        open={!!deleteId}
        onOpenChange={() => setDeleteId(null)}
        title="删除节点"
        description="确定要删除此节点吗？"
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
