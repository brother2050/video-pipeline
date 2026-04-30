import { StageType } from "@/types";

interface CandidateDetailProps {
  content: Record<string, unknown>;
  stageType: StageType;
}

interface Character {
  name: string;
  role: string;
  description: string;
  personality: string;
  appearance: string;
  arc: string;
}

interface Episode {
  number: number;
  title: string;
  summary: string;
  scene_names?: string[];
}

interface PlotArc {
  name: string;
  description: string;
  episodes_span: string;
}

interface Scene {
  scene_number: number;
  episode_ref: number;
  location: string;
  time_of_day: string;
  characters_present?: string[];
  action: string;
  dialogue?: Array<{
    character: string;
    line: string;
  }>;
}

interface Shot {
  shot_number: number;
  scene_ref: number;
  camera_angle: string;
  camera_movement: string;
  duration_sec: number;
  description: string;
  image_prompt?: string;
}

interface VoiceCast {
  voice_id: string;
  voice_style: string;
}

interface DialoguePlan {
  character: string;
  text?: string;
  scene_ref: number;
  emotion: string;
  start_sec: number;
}

interface BgmPlan {
  scene_ref: number;
  style: string;
  mood: string;
  duration_sec: number;
}

interface SfxPlan {
  scene_ref: number;
  description: string;
  start_sec: number;
  duration_sec: number;
}

export function CandidateDetail({ content, stageType }: CandidateDetailProps) {
  const formatContent = () => {
    switch (stageType) {
      case StageType.WORLDBUILDING:
        return formatWorldBuilding(content);
      case StageType.OUTLINE:
        return formatOutline(content);
      case StageType.SCRIPT:
        return formatScript(content);
      case StageType.STORYBOARD:
        return formatStoryboard(content);
      case StageType.AUDIO:
        return formatAudio(content);
      default:
        return <pre className="text-xs whitespace-pre-wrap">{JSON.stringify(content, null, 2)}</pre>;
    }
  };

  const formatWorldBuilding = (data: Record<string, unknown>) => {
    const characters = data.characters as Character[] | undefined;
    const worldBible = data.world_bible as string | undefined;
    
    return (
      <div className="space-y-4">
        {worldBible && (
          <div>
            <h5 className="text-xs font-semibold mb-2 text-primary">世界设定</h5>
            <p className="text-xs text-muted-foreground whitespace-pre-wrap">{worldBible}</p>
          </div>
        )}
        {characters && characters.length > 0 && (
          <div>
            <h5 className="text-xs font-semibold mb-2 text-primary">角色信息</h5>
            <div className="space-y-2">
              {characters.map((char, idx) => (
                <div key={idx} className="text-xs border-l-2 border-muted pl-2">
                  <div className="font-medium">{char.name} <span className="text-muted-foreground">({char.role})</span></div>
                  <div className="text-muted-foreground mt-1">{char.description}</div>
                  <div className="text-muted-foreground mt-1">性格: {char.personality}</div>
                  <div className="text-muted-foreground mt-1">外貌: {char.appearance}</div>
                  <div className="text-muted-foreground mt-1">角色弧: {char.arc}</div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  const formatOutline = (data: Record<string, unknown>) => {
    const episodes = data.episodes as Episode[] | undefined;
    const plotArcs = data.plot_arcs as PlotArc[] | undefined;
    
    return (
      <div className="space-y-4">
        {episodes && episodes.length > 0 && (
          <div>
            <h5 className="text-xs font-semibold mb-2 text-primary">剧集列表</h5>
            <div className="space-y-2">
              {episodes.map((ep, idx) => (
                <div key={idx} className="text-xs border-l-2 border-muted pl-2">
                  <div className="font-medium">第 {ep.number} 集: {ep.title}</div>
                  <div className="text-muted-foreground mt-1">{ep.summary}</div>
                  <div className="text-muted-foreground mt-1">场景: {ep.scene_names?.join(", ")}</div>
                </div>
              ))}
            </div>
          </div>
        )}
        {plotArcs && plotArcs.length > 0 && (
          <div>
            <h5 className="text-xs font-semibold mb-2 text-primary">情节弧</h5>
            <div className="space-y-2">
              {plotArcs.map((arc, idx) => (
                <div key={idx} className="text-xs border-l-2 border-muted pl-2">
                  <div className="font-medium">{arc.name}</div>
                  <div className="text-muted-foreground mt-1">{arc.description}</div>
                  <div className="text-muted-foreground mt-1">跨度: {arc.episodes_span}</div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  const formatScript = (data: Record<string, unknown>) => {
    const scenes = data.scenes as Scene[] | undefined;
    
    return (
      <div className="space-y-4">
        {scenes && scenes.length > 0 && (
          <div>
            <h5 className="text-xs font-semibold mb-2 text-primary">场景列表</h5>
            <div className="space-y-3">
              {scenes.slice(0, 5).map((scene, idx) => (
                <div key={idx} className="text-xs border-l-2 border-muted pl-2">
                  <div className="font-medium">场景 {scene.scene_number} <span className="text-muted-foreground">| 第 {scene.episode_ref} 集</span></div>
                  <div className="text-muted-foreground mt-1">地点: {scene.location} | 时间: {scene.time_of_day}</div>
                  <div className="text-muted-foreground mt-1">人物: {scene.characters_present?.join(", ")}</div>
                  <div className="text-muted-foreground mt-1">动作: {scene.action}</div>
                  {scene.dialogue && scene.dialogue.length > 0 && (
                    <div className="mt-2 space-y-1">
                      {scene.dialogue.map((dialogue, dIdx) => (
                        <div key={dIdx} className="pl-2 border-l border-muted">
                          <span className="font-medium">{dialogue.character}:</span> {dialogue.line}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))}
              {scenes.length > 5 && (
                <div className="text-xs text-muted-foreground text-center">... 还有 {scenes.length - 5} 个场景</div>
              )}
            </div>
          </div>
        )}
      </div>
    );
  };

  const formatStoryboard = (data: Record<string, unknown>) => {
    const shots = data.shots as Shot[] | undefined;
    
    return (
      <div className="space-y-4">
        {shots && shots.length > 0 && (
          <div>
            <h5 className="text-xs font-semibold mb-2 text-primary">镜头列表</h5>
            <div className="space-y-3">
              {shots.slice(0, 5).map((shot, idx) => (
                <div key={idx} className="text-xs border-l-2 border-muted pl-2">
                  <div className="font-medium">镜头 {shot.shot_number} <span className="text-muted-foreground">| 场景 {shot.scene_ref}</span></div>
                  <div className="text-muted-foreground mt-1">角度: {shot.camera_angle} | 运镜: {shot.camera_movement}</div>
                  <div className="text-muted-foreground mt-1">时长: {shot.duration_sec}秒</div>
                  <div className="text-muted-foreground mt-1">描述: {shot.description}</div>
                  <div className="text-muted-foreground mt-1">图像提示: {shot.image_prompt?.slice(0, 100)}...</div>
                </div>
              ))}
              {shots.length > 5 && (
                <div className="text-xs text-muted-foreground text-center">... 还有 {shots.length - 5} 个镜头</div>
              )}
            </div>
          </div>
        )}
      </div>
    );
  };

  const formatAudio = (data: Record<string, unknown>) => {
    const voiceCast = data.voice_cast as Record<string, VoiceCast> | undefined;
    const dialoguePlan = data.dialogue_plan as DialoguePlan[] | undefined;
    const bgmPlan = data.bgm_plan as BgmPlan[] | undefined;
    const sfxPlan = data.sfx_plan as SfxPlan[] | undefined;
    
    return (
      <div className="space-y-4">
        {voiceCast && Object.keys(voiceCast).length > 0 && (
          <div>
            <h5 className="text-xs font-semibold mb-2 text-primary">配音阵容</h5>
            <div className="space-y-2">
              {Object.entries(voiceCast).map(([char, voice], idx) => (
                <div key={idx} className="text-xs border-l-2 border-muted pl-2">
                  <div className="font-medium">{char}</div>
                  <div className="text-muted-foreground">声音ID: {voice.voice_id} | 风格: {voice.voice_style}</div>
                </div>
              ))}
            </div>
          </div>
        )}
        {dialoguePlan && dialoguePlan.length > 0 && (
          <div>
            <h5 className="text-xs font-semibold mb-2 text-primary">对话计划</h5>
            <div className="space-y-2">
              {dialoguePlan.slice(0, 5).map((dialogue, idx) => (
                <div key={idx} className="text-xs border-l-2 border-muted pl-2">
                  <div className="font-medium">{dialogue.character}: {dialogue.text?.slice(0, 50)}...</div>
                  <div className="text-muted-foreground">场景 {dialogue.scene_ref} | 情绪: {dialogue.emotion} | 开始时间: {dialogue.start_sec}s</div>
                </div>
              ))}
              {dialoguePlan.length > 5 && (
                <div className="text-xs text-muted-foreground text-center">... 还有 {dialoguePlan.length - 5} 条对话</div>
              )}
            </div>
          </div>
        )}
        {bgmPlan && bgmPlan.length > 0 && (
          <div>
            <h5 className="text-xs font-semibold mb-2 text-primary">背景音乐</h5>
            <div className="space-y-2">
              {bgmPlan.slice(0, 3).map((bgm, idx) => (
                <div key={idx} className="text-xs border-l-2 border-muted pl-2">
                  <div className="font-medium">场景 {bgm.scene_ref}</div>
                  <div className="text-muted-foreground">风格: {bgm.style} | 情绪: {bgm.mood} | 时长: {bgm.duration_sec}s</div>
                </div>
              ))}
            </div>
          </div>
        )}
        {sfxPlan && sfxPlan.length > 0 && (
          <div>
            <h5 className="text-xs font-semibold mb-2 text-primary">音效计划</h5>
            <div className="space-y-2">
              {sfxPlan.slice(0, 3).map((sfx, idx) => (
                <div key={idx} className="text-xs border-l-2 border-muted pl-2">
                  <div className="font-medium">场景 {sfx.scene_ref}</div>
                  <div className="text-muted-foreground">描述: {sfx.description} | 开始时间: {sfx.start_sec}s | 时长: {sfx.duration_sec}s</div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="overflow-auto max-h-96">
      {formatContent()}
    </div>
  );
}