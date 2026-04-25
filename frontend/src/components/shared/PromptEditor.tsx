/**
 * 提示词编辑器组件
 */

import { useState } from "react";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { Save, Loader2 } from "lucide-react";

interface PromptEditorProps {
  value: string;
  onSave: (prompt: string) => void;
  disabled?: boolean;
}

export function PromptEditor({ value, onSave, disabled }: PromptEditorProps) {
  const [localValue, setLocalValue] = useState(value);
  const [saving, setSaving] = useState(false);

  const handleSave = async () => {
    setSaving(true);
    try {
      onSave(localValue);
    } finally {
      setSaving(false);
    }
  };

  const hasChanges = localValue !== value;

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium text-muted-foreground">提示词</span>
        {hasChanges && !disabled && (
          <Button size="sm" variant="ghost" className="h-6 text-xs" onClick={handleSave} disabled={saving}>
            {saving ? <Loader2 className="h-3 w-3 mr-1 animate-spin" /> : <Save className="h-3 w-3 mr-1" />}
            保存
          </Button>
        )}
      </div>
      <Textarea
        value={localValue}
        onChange={(e) => setLocalValue(e.target.value)}
        disabled={disabled}
        rows={6}
        className="text-xs font-mono resize-y"
        placeholder="输入提示词..."
      />
    </div>
  );
}
