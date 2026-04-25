/**
 * 系统设置页
 */

import { useSystemStatus } from "@/hooks/useApi";
import { Card } from "@/components/ui/card";
import { useUIStore } from "@/stores/uiStore";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";

export default function Settings() {
  const { data: status } = useSystemStatus();
  const theme = useUIStore((s) => s.theme);
  const setTheme = useUIStore((s) => s.setTheme);

  return (
    <div className="space-y-6 max-w-2xl">
      <h1 className="text-2xl font-semibold">系统设置</h1>

      <Card className="p-4 space-y-4">
        <h3 className="font-medium">外观</h3>
        <div className="flex items-center justify-between">
          <Label>深色模式</Label>
          <Switch checked={theme === "dark"} onCheckedChange={(checked) => setTheme(checked ? "dark" : "light")} />
        </div>
      </Card>

      <Card className="p-4 space-y-4">
        <h3 className="font-medium">系统信息</h3>
        {status && (
          <div className="grid grid-cols-2 gap-2 text-sm">
            <span className="text-muted-foreground">运行时间</span>
            <span>{Math.floor(status.uptime_seconds / 3600)}h {Math.floor((status.uptime_seconds % 3600) / 60)}m</span>
            <span className="text-muted-foreground">项目总数</span>
            <span>{status.total_projects}</span>
            <span className="text-muted-foreground">节点总数</span>
            <span>{status.total_nodes}</span>
            <span className="text-muted-foreground">在线节点</span>
            <span>{status.online_nodes}</span>
          </div>
        )}
      </Card>

      <Card className="p-4 space-y-4">
        <h3 className="font-medium">供应商健康</h3>
        {status && (
          <div className="grid grid-cols-2 gap-2 text-sm">
            {Object.entries(status.supplier_health).map(([cap, health]) => (
              <div key={cap} className="flex items-center justify-between">
                <span className="text-muted-foreground">{cap}</span>
                <span className={health === "ok" ? "text-green-600" : health === "degraded" ? "text-yellow-600" : "text-red-600"}>
                  {health}
                </span>
              </div>
            ))}
          </div>
        )}
      </Card>

      <Card className="p-4 space-y-2">
        <h3 className="font-medium">配置参考</h3>
        <p className="text-sm text-muted-foreground">
          配置文件位于 <code className="bg-secondary px-1 rounded">config/</code> 目录下：
        </p>
        <ul className="text-sm text-muted-foreground list-disc pl-5 space-y-1">
          <li><code>default.yaml</code> — 服务端口、数据库、心跳等基础配置</li>
          <li><code>nodes.yaml</code> — 节点列表</li>
          <li><code>suppliers.yaml</code> — 供应商配置</li>
        </ul>
        <p className="text-sm text-muted-foreground">
          修改配置后通过 Web 页面保存即可生效，无需重启服务。
        </p>
      </Card>
    </div>
  );
}
