/**
 * 供应商配置页
 * - 按能力分 Tab 页
 * - 每个 Tab 内：供应商列表 + 配置表单 + 测试连接
 * - ComfyUI 支持导入工作流 JSON
 */

import { useState } from "react";
import { useSuppliers, useUpdateSupplier, useTestSupplier } from "@/hooks/useSuppliers";
import { useProviders, useCapabilityLabels } from "@/hooks/useConstants";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { WorkflowUploader } from "@/components/shared/WorkflowUploader";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Loader2, TestTube, Save, Plus, Trash2, ArrowUp, ArrowDown } from "lucide-react";
import { SupplierCapability } from "@/types";
import type { SupplierSlot, CapabilityConfigResponse } from "@/types";

export default function SupplierConfig() {
  const { data: capabilityLabels } = useCapabilityLabels();
  const { data: configs, isLoading } = useSuppliers();
  
  const CAP_TABS: { value: SupplierCapability; label: string }[] = Object.entries(capabilityLabels || {}).map(([value, label]) => ({
    value: value as SupplierCapability,
    label
  }));

  if (isLoading) {
    return <div className="text-center py-12 text-muted-foreground">加载中...</div>;
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">供应商配置</h1>

      <Tabs defaultValue={SupplierCapability.LLM}>
        <TabsList>
          {CAP_TABS.map((tab) => (
            <TabsTrigger key={tab.value} value={tab.value}>{tab.label}</TabsTrigger>
          ))}
        </TabsList>

        {CAP_TABS.map((tab) => {
          const config = configs?.find((c) => c.capability === tab.value);
          return (
            <TabsContent key={tab.value} value={tab.value}>
              <CapabilityTab capability={tab.value} config={config} />
            </TabsContent>
          );
        })}
      </Tabs>
    </div>
  );
}

function CapabilityTab({ capability, config }: { capability: SupplierCapability; config?: CapabilityConfigResponse }) {
  const { data: providers } = useProviders(capability);
  const updateMut = useUpdateSupplier(capability);
  const testMut = useTestSupplier();

  const [localConfig, setLocalConfig] = useState<CapabilityConfigResponse>(
    config ?? { capability, suppliers: [], retry_count: 2, timeout_seconds: 60, local_timeout_seconds: 300 }
  );

  const addSupplier = () => {
    setLocalConfig((prev) => ({
      ...prev,
      suppliers: [...prev.suppliers, {
        provider: "", model: "", base_url: "",
        api_key: "", is_local: false, priority: prev.suppliers.length + 1,
        extra_params: {},
      }],
    }));
  };

  const removeSupplier = (idx: number) => {
    setLocalConfig((prev) => ({
      ...prev,
      suppliers: prev.suppliers.filter((_, i) => i !== idx),
    }));
  };

  const updateSlot = (idx: number, field: keyof SupplierSlot, value: unknown) => {
    setLocalConfig((prev) => ({
      ...prev,
      suppliers: prev.suppliers.map((s, i) => i === idx ? { ...s, [field]: value } : s),
    }));
  };

  const moveSlot = (idx: number, direction: -1 | 1) => {
    setLocalConfig((prev) => {
      const newSuppliers = [...prev.suppliers];
      const targetIdx = idx + direction;
      if (targetIdx < 0 || targetIdx >= newSuppliers.length) return prev;
      const temp = newSuppliers[idx]!;
      newSuppliers[idx] = newSuppliers[targetIdx]!;
      newSuppliers[targetIdx] = temp;
      newSuppliers.forEach((s, i) => { s.priority = i + 1; });
      return { ...prev, suppliers: newSuppliers };
    });
  };

  const handleSave = async () => {
    await updateMut.mutateAsync({
      suppliers: localConfig.suppliers,
      retry_count: localConfig.retry_count,
      timeout_seconds: localConfig.timeout_seconds,
      local_timeout_seconds: localConfig.local_timeout_seconds,
    });
  };

  const handleTest = async (slot: SupplierSlot) => {
    await testMut.mutateAsync({ capability, slot });
  };

  const handleWorkflowUploaded = (path: string) => {
    setLocalConfig((prev) => ({
      ...prev,
      suppliers: prev.suppliers.map((s) =>
        s.provider === "comfyui" || s.provider === "comfyui_video"
          ? { ...s, extra_params: { ...s.extra_params, workflow_template: path } }
          : s
      ),
    }));
  };

  const isComfyCap = capability === SupplierCapability.IMAGE || capability === SupplierCapability.VIDEO;

  return (
    <div className="space-y-4">
      {/* 全局配置 */}
      <Card className="p-4">
        <h3 className="text-sm font-medium mb-3">全局参数</h3>
        <div className="grid grid-cols-3 gap-4">
          <div>
            <Label className="text-xs">重试次数</Label>
            <Input type="number" min={0} max={10} value={localConfig.retry_count}
              onChange={(e) => setLocalConfig({ ...localConfig, retry_count: parseInt(e.target.value) || 0 })} className="h-8" />
          </div>
          <div>
            <Label className="text-xs">远程超时(秒)</Label>
            <Input type="number" min={5} value={localConfig.timeout_seconds}
              onChange={(e) => setLocalConfig({ ...localConfig, timeout_seconds: parseInt(e.target.value) || 60 })} className="h-8" />
          </div>
          <div>
            <Label className="text-xs">本地超时(秒)</Label>
            <Input type="number" min={10} value={localConfig.local_timeout_seconds}
              onChange={(e) => setLocalConfig({ ...localConfig, local_timeout_seconds: parseInt(e.target.value) || 300 })} className="h-8" />
          </div>
        </div>
      </Card>

      {/* ComfyUI 工作流导入 */}
      {isComfyCap && (
        <Card className="p-4">
          <h3 className="text-sm font-medium mb-3">ComfyUI 工作流模板</h3>
          <WorkflowUploader onUploaded={handleWorkflowUploaded} />
        </Card>
      )}

      {/* 供应商列表 */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-medium">供应商列表（按优先级排序）</h3>
          <Button size="sm" variant="outline" onClick={addSupplier}>
            <Plus className="h-3 w-3 mr-1" />添加
          </Button>
        </div>

        {localConfig.suppliers.map((slot, idx) => (
          <Card key={idx} className="p-4">
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center gap-2">
                <Badge variant="outline">优先级 {slot.priority}</Badge>
                {slot.is_local && <Badge variant="secondary">本地</Badge>}
              </div>
              <div className="flex gap-1">
                <Button variant="ghost" size="sm" disabled={idx === 0} onClick={() => moveSlot(idx, -1)}>
                  <ArrowUp className="h-3 w-3" />
                </Button>
                <Button variant="ghost" size="sm" disabled={idx === localConfig.suppliers.length - 1} onClick={() => moveSlot(idx, 1)}>
                  <ArrowDown className="h-3 w-3" />
                </Button>
                <Button variant="ghost" size="sm" className="text-destructive" onClick={() => removeSupplier(idx)}>
                  <Trash2 className="h-3 w-3" />
                </Button>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <Label className="text-xs">Provider</Label>
                <Select value={slot.provider} onValueChange={(v) => updateSlot(idx, "provider", v)}>
                  <SelectTrigger className="h-8">
                    <SelectValue placeholder="选择 Provider" />
                  </SelectTrigger>
                  <SelectContent>
                    {(providers || []).map((p) => (
                      <SelectItem key={p} value={p}>{p}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label className="text-xs">Model</Label>
                <Input value={slot.model} onChange={(e) => updateSlot(idx, "model", e.target.value)} className="h-8" />
              </div>
              <div>
                <Label className="text-xs">Base URL</Label>
                <Input value={slot.base_url || ""} onChange={(e) => updateSlot(idx, "base_url", e.target.value)} className="h-8" placeholder="http://localhost:8188" />
              </div>
              <div>
                <Label className="text-xs">API Key</Label>
                <Input type="password" value={slot.api_key || ""} onChange={(e) => updateSlot(idx, "api_key", e.target.value)} className="h-8" />
              </div>
            </div>

            <div className="flex items-center gap-4 mt-3">
              <label className="flex items-center gap-2 text-xs">
                <input type="checkbox" checked={slot.is_local} onChange={(e) => updateSlot(idx, "is_local", e.target.checked)} />
                本地服务
              </label>
              <Button size="sm" variant="outline" onClick={() => handleTest(slot)} disabled={testMut.isPending}>
                {testMut.isPending ? <Loader2 className="h-3 w-3 mr-1 animate-spin" /> : <TestTube className="h-3 w-3 mr-1" />}
                测试连接
              </Button>
            </div>
          </Card>
        ))}

        {localConfig.suppliers.length === 0 && (
          <p className="text-sm text-muted-foreground text-center py-4">暂无供应商，点击添加</p>
        )}
      </div>

      {/* 测试结果 */}
      {testMut.data && (
        <Card className={`p-3 ${testMut.data.success ? "border-green-500" : "border-red-500"} border`}>
          <p className="text-sm">{testMut.data.success ? "连接成功" : "连接失败"}</p>
          <p className="text-xs text-muted-foreground">延迟: {testMut.data.latency_ms}ms</p>
          {testMut.data.response_preview && <p className="text-xs text-muted-foreground">{testMut.data.response_preview}</p>}
          {testMut.data.error && <p className="text-xs text-red-500">{testMut.data.error}</p>}
        </Card>
      )}

      {/* 保存 */}
      <Button onClick={handleSave} disabled={updateMut.isPending}>
        {updateMut.isPending ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <Save className="h-4 w-4 mr-2" />}
        保存配置
      </Button>
    </div>
  );
}