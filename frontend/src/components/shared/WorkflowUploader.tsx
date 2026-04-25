import { useState, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Upload, FileJson, Loader2 } from "lucide-react";
import { useAnalyzeWorkflow, useUploadWorkflow } from "@/hooks/useSuppliers";
import { WorkflowAnalysisView } from "./WorkflowAnalysisView";
import type { WorkflowAnalysis } from "@/types";

interface WorkflowUploaderProps {
  onUploaded: (path: string, analysis: WorkflowAnalysis) => void;
}

export function WorkflowUploader({ onUploaded }: WorkflowUploaderProps) {
  const fileRef = useRef<HTMLInputElement>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [analysis, setAnalysis] = useState<WorkflowAnalysis | null>(null);
  const [pendingFile, setPendingFile] = useState<File | null>(null);

  const analyzeMutation = useAnalyzeWorkflow();
  const uploadMutation = useUploadWorkflow();

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setPendingFile(file);
    setAnalyzing(true);

    try {
      const text = await file.text();
      const workflow = JSON.parse(text) as Record<string, unknown>;
      const result = await analyzeMutation.mutateAsync(workflow);
      setAnalysis(result);
    } catch (err) {
      console.error("Failed to analyze workflow:", err);
    } finally {
      setAnalyzing(false);
    }
  };

  const handleConfirm = async () => {
    if (!pendingFile || !analysis) return;
    try {
      const result = await uploadMutation.mutateAsync(pendingFile);
      onUploaded(result.path, analysis);
      setAnalysis(null);
      setPendingFile(null);
    } catch (err) {
      console.error("Failed to upload workflow:", err);
    }
  };

  return (
    <div className="space-y-4">
      <input
        ref={fileRef}
        type="file"
        accept=".json"
        className="hidden"
        onChange={handleFileChange}
      />

      <Button variant="outline" onClick={() => fileRef.current?.click()} disabled={analyzing}>
        {analyzing ? (
          <Loader2 className="h-4 w-4 mr-2 animate-spin" />
        ) : (
          <Upload className="h-4 w-4 mr-2" />
        )}
        导入 ComfyUI 工作流 JSON
      </Button>

      {pendingFile && !analysis && !analyzing && (
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <FileJson className="h-4 w-4" />
          <span>{pendingFile.name}</span>
        </div>
      )}

      {analysis && (
        <div className="space-y-4">
          <WorkflowAnalysisView analysis={analysis} />
          <div className="flex gap-2">
            <Button size="sm" onClick={handleConfirm} disabled={uploadMutation.isPending}>
              {uploadMutation.isPending ? <Loader2 className="h-3 w-3 mr-1 animate-spin" /> : null}
              确认使用
            </Button>
            <Button size="sm" variant="outline" onClick={() => { setAnalysis(null); setPendingFile(null); }}>
              取消
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
