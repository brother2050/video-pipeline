/**
 * 项目设置页
 * 分组展示所有项目级配置，修改即时保存。
 */

import { useParams } from "react-router-dom";
import { useProject } from "@/hooks/useProjects";
import { useProjectSettings, useUpdateProjectSettings } from "@/hooks/useProjects";
import {
  useResolutions,
  useSubtitlePositions,
  useAudioCodecs,
  useVideoBitrates,
  useAudioBitrates,
  useFonts,
  useSubtitleColors,
} from "@/hooks/useConstants";
import { ProjectNav } from "@/components/layout/ProjectNav";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Separator } from "@/components/ui/separator";
import { Loader2, Save } from "lucide-react";
import { useState, useEffect } from "react";
import type { ProjectSettingResponse, ProjectSettingUpdate } from "@/types";

export default function ProjectSettingsPage() {
  const { id } = useParams<{ id: string }>();
  const { data: project } = useProject(id || "");
  const { data: settings, isLoading } = useProjectSettings(id || "");
  const updateMut = useUpdateProjectSettings(id || "");

  const { data: resolutions } = useResolutions();
  const { data: subtitlePositions } = useSubtitlePositions();
  const { data: audioCodecs } = useAudioCodecs();
  const { data: videoBitrates } = useVideoBitrates();
  const { data: audioBitrates } = useAudioBitrates();
  const { data: fonts } = useFonts();
  const { data: subtitleColors } = useSubtitleColors();

  const [form, setForm] = useState<ProjectSettingUpdate>({});
  const [dirty, setDirty] = useState(false);

  useEffect(() => {
    if (settings) {
      setForm({});
      setDirty(false);
    }
  }, [settings]);

  if (isLoading || !settings || !id) {
    return <div className="text-center py-12 text-muted-foreground">加载中...</div>;
  }

  const s: ProjectSettingResponse = settings;

  const updateField = <K extends keyof ProjectSettingUpdate>(key: K, value: ProjectSettingUpdate[K]) => {
    setForm((prev) => ({ ...prev, [key]: value }));
    setDirty(true);
  };

  const current = <K extends keyof ProjectSettingResponse>(key: K): ProjectSettingResponse[K] => {
    return (form[key as keyof ProjectSettingUpdate] as ProjectSettingResponse[K] | undefined) ?? s[key];
  };

  const handleSave = async () => {
    await updateMut.mutateAsync(form);
    setDirty(false);
  };

  return (
    <div className="space-y-4">
      <div>
        <p className="text-sm text-muted-foreground">{project?.name}</p>
        <ProjectNav />
      </div>

      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">项目设置</h1>
        <Button onClick={handleSave} disabled={!dirty || updateMut.isPending}>
          {updateMut.isPending ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <Save className="h-4 w-4 mr-2" />}
          保存
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

        {/* 生成默认值 */}
        <Card className="p-5 space-y-4">
          <h3 className="font-medium">生成默认值</h3>
          <Separator />

          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label className="text-xs">默认候选数量</Label>
              <Input type="number" min={1} max={10}
                value={current("default_num_candidates")}
                onChange={(e) => updateField("default_num_candidates", parseInt(e.target.value) || 3)}
                className="h-8" />
            </div>
            <div>
              <Label className="text-xs">默认视频时长(秒)</Label>
              <Input type="number" min={1} max={300} step={0.5}
                value={current("video_duration_sec")}
                onChange={(e) => updateField("video_duration_sec", parseFloat(e.target.value) || 5)}
                className="h-8" />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label className="text-xs">图片宽度</Label>
              <Input type="number" min={256} max={4096}
                value={current("image_width")}
                onChange={(e) => updateField("image_width", parseInt(e.target.value) || 1536)}
                className="h-8" />
            </div>
            <div>
              <Label className="text-xs">图片高度</Label>
              <Input type="number" min={256} max={4096}
                value={current("image_height")}
                onChange={(e) => updateField("image_height", parseInt(e.target.value) || 864)}
                className="h-8" />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label className="text-xs">视频分辨率</Label>
              <Select value={current("video_resolution")} onValueChange={(v) => updateField("video_resolution", v)}>
                <SelectTrigger className="h-8">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {(resolutions || []).map((r) => (
                    <SelectItem key={r} value={r}>{r}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label className="text-xs">帧率(FPS)</Label>
              <Input type="number" min={1} max={120}
                value={current("video_fps")}
                onChange={(e) => updateField("video_fps", parseInt(e.target.value) || 24)}
                className="h-8" />
            </div>
          </div>
        </Card>

        {/* 音频默认值 */}
        <Card className="p-5 space-y-4">
          <h3 className="font-medium">音频默认值</h3>
          <Separator />

          <div>
            <Label className="text-xs">TTS 语音</Label>
            <Input value={current("default_tts_voice")}
              onChange={(e) => updateField("default_tts_voice", e.target.value)}
              className="h-8" placeholder="default" />
          </div>

          <div>
            <Label className="text-xs">背景音乐风格</Label>
            <Input value={current("default_bgm_style")}
              onChange={(e) => updateField("default_bgm_style", e.target.value)}
              className="h-8" placeholder="例如：轻松、紧张" />
          </div>

          <div>
            <Label className="text-xs">音效库</Label>
            <Input value={current("default_sfx_library")}
              onChange={(e) => updateField("default_sfx_library", e.target.value)}
              className="h-8" placeholder="音效库路径" />
          </div>
        </Card>

        {/* 输出设置 */}
        <Card className="p-5 space-y-4">
          <h3 className="font-medium">输出设置</h3>
          <Separator />

          <div className="grid grid-cols-3 gap-4">
            <div>
              <Label className="text-xs">视频码率</Label>
              <Select value={current("output_bitrate")} onValueChange={(v) => updateField("output_bitrate", v)}>
                <SelectTrigger className="h-8">
                  <SelectValue placeholder="选择码率" />
                </SelectTrigger>
                <SelectContent>
                  {(videoBitrates || []).map((b) => (
                    <SelectItem key={b} value={b}>{b}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label className="text-xs">音频编码</Label>
              <Select value={current("output_audio_codec")} onValueChange={(v) => updateField("output_audio_codec", v)}>
                <SelectTrigger className="h-8">
                  <SelectValue placeholder="选择编码" />
                </SelectTrigger>
                <SelectContent>
                  {(audioCodecs || []).map((c) => (
                    <SelectItem key={c} value={c}>{c}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label className="text-xs">音频码率</Label>
              <Select value={current("output_audio_bitrate")} onValueChange={(v) => updateField("output_audio_bitrate", v)}>
                <SelectTrigger className="h-8">
                  <SelectValue placeholder="选择码率" />
                </SelectTrigger>
                <SelectContent>
                  {(audioBitrates || []).map((b) => (
                    <SelectItem key={b} value={b}>{b}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
        </Card>

        {/* 字幕设置 */}
        <Card className="p-5 space-y-4">
          <h3 className="font-medium">字幕设置</h3>
          <Separator />

          <div className="flex items-center justify-between">
            <Label className="text-xs">启用字幕</Label>
            <Switch checked={current("subtitle_enabled")}
              onCheckedChange={(v) => updateField("subtitle_enabled", v)} />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label className="text-xs">字体</Label>
              <Select value={current("subtitle_font")} onValueChange={(v) => updateField("subtitle_font", v)}>
                <SelectTrigger className="h-8">
                  <SelectValue placeholder="选择字体" />
                </SelectTrigger>
                <SelectContent>
                  {(fonts || []).map((f) => (
                    <SelectItem key={f} value={f}>{f}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label className="text-xs">字号</Label>
              <Input type="number" min={12} max={120}
                value={current("subtitle_size")}
                onChange={(e) => updateField("subtitle_size", parseInt(e.target.value) || 48)}
                className="h-8" />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label className="text-xs">颜色</Label>
              <Select value={current("subtitle_color")} onValueChange={(v) => updateField("subtitle_color", v)}>
                <SelectTrigger className="h-8">
                  <SelectValue placeholder="选择颜色" />
                </SelectTrigger>
                <SelectContent>
                  {(subtitleColors || []).map((c) => (
                    <SelectItem key={c} value={c}>{c}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label className="text-xs">位置</Label>
              <Select value={current("subtitle_position")} onValueChange={(v) => updateField("subtitle_position", v)}>
                <SelectTrigger className="h-8">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {(subtitlePositions || []).map((p) => (
                    <SelectItem key={p} value={p}>{p}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
        </Card>

        {/* 调色设置 */}
        <Card className="p-5 space-y-4">
          <h3 className="font-medium">调色设置</h3>
          <Separator />

          <div>
            <Label className="text-xs">LUT 路径</Label>
            <Input value={current("color_grade_lut")}
              onChange={(e) => updateField("color_grade_lut", e.target.value)}
              className="h-8" placeholder="LUT 文件路径" />
          </div>

          <div>
            <Label className="text-xs">调色强度 ({current("color_grade_intensity")})</Label>
            <input
              type="range"
              min={0}
              max={1}
              step={0.1}
              value={current("color_grade_intensity")}
              onChange={(e) => updateField("color_grade_intensity", parseFloat(e.target.value))}
              className="w-full h-2 bg-secondary rounded-lg appearance-none cursor-pointer"
            />
          </div>

          <div>
            <Label className="text-xs">暗角强度 ({current("vignette_intensity")})</Label>
            <input
              type="range"
              min={0}
              max={1}
              step={0.1}
              value={current("vignette_intensity")}
              onChange={(e) => updateField("vignette_intensity", parseFloat(e.target.value))}
              className="w-full h-2 bg-secondary rounded-lg appearance-none cursor-pointer"
            />
          </div>

          <div>
            <Label className="text-xs">噪点强度 ({current("grain_intensity")})</Label>
            <input
              type="range"
              min={0}
              max={1}
              step={0.05}
              value={current("grain_intensity")}
              onChange={(e) => updateField("grain_intensity", parseFloat(e.target.value))}
              className="w-full h-2 bg-secondary rounded-lg appearance-none cursor-pointer"
            />
          </div>
        </Card>

        {/* ComfyUI 工作流 */}
        <Card className="p-5 space-y-4">
          <h3 className="font-medium">ComfyUI 工作流</h3>
          <Separator />

          <div>
            <Label className="text-xs">工作流路径</Label>
            <Input value={current("comfyui_workflow_path")}
              onChange={(e) => updateField("comfyui_workflow_path", e.target.value)}
              className="h-8" placeholder="ComfyUI 工作流 JSON 文件路径" />
          </div>
        </Card>

      </div>
    </div>
  );
}