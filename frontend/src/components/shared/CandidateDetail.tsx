import { StageType } from "@/types";

interface CandidateDetailProps {
  content: Record<string, any>;
  stageType: StageType;
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

  const formatWorldBuilding = (data: any) => (
    <div className="space-y-4">
      {data.world_bible && (
        <div>
          <h5 className="text-xs font-semibold mb-2 text-primary">世界设定</h5>
          <p className="text-xs text-muted-foreground whitespace-pre-wrap">{data.world_bible}</p>
        </div>
      )}
      {data.characters && data.characters.length > 0 && (
        <div>
          <h5 className="text-xs font-semibold mb-2 text-primary">角色信息</h5>
          <div className="space-y-2">
            {data.characters.map((char: any, idx: number) => (
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

  const formatOutline = (data: any) => (
    <div className="space-y-4">
      {data.episodes && data.episodes.length > 0 && (
        <div>
          <h5 className="text-xs font-semibold mb-2 text-primary">剧集列表</h5>
          <div className="space-y-2">
            {data.episodes.map((ep: any, idx: number) => (
              <div key={idx} className="text-xs border-l-2 border-muted pl-2">
                <div className="font-medium">第 {ep.number} 集: {ep.title}</div>
                <div className="text-muted-foreground mt-1">{ep.summary}</div>
                <div className="text-muted-foreground mt-1">场景: {ep.scene_names?.join(", ")}</div>
              </div>
            ))}
          </div>
        </div>
      )}
      {data.plot_arcs && data.plot_arcs.length > 0 && (
        <div>
          <h5 className="text-xs font-semibold mb-2 text-primary">情节弧</h5>
          <div className="space-y-2">
            {data.plot_arcs.map((arc: any, idx: number) => (
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

  const formatScript = (data: any) => (
    <div className="space-y-4">
      {data.scenes && data.scenes.length > 0 && (
        <div>
          <h5 className="text-xs font-semibold mb-2 text-primary">场景列表</h5>
          <div className="space-y-3">
            {data.scenes.slice(0, 5).map((scene: any, idx: number) => (
              <div key={idx} className="text-xs border-l-2 border-muted pl-2">
                <div className="font-medium">场景 {scene.scene_number} <span className="text-muted-foreground">| 第 {scene.episode_ref} 集</span></div>
                <div className="text-muted-foreground mt-1">地点: {scene.location} | 时间: {scene.time_of_day}</div>
                <div className="text-muted-foreground mt-1">人物: {scene.characters_present?.join(", ")}</div>
                <div className="text-muted-foreground mt-1">动作: {scene.action}</div>
                {scene.dialogue && scene.dialogue.length > 0 && (
                  <div className="mt-2 space-y-1">
                    {scene.dialogue.map((dialogue: any, dIdx: number) => (
                      <div key={dIdx} className="pl-2 border-l border-muted">
                        <span className="font-medium">{dialogue.character}:</span> {dialogue.line}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}
            {data.scenes.length > 5 && (
              <div className="text-xs text-muted-foreground text-center">... 还有 {data.scenes.length - 5} 个场景</div>
            )}
          </div>
        </div>
      )}
    </div>
  );

  const formatStoryboard = (data: any) => (
    <div className="space-y-4">
      {data.shots && data.shots.length > 0 && (
        <div>
          <h5 className="text-xs font-semibold mb-2 text-primary">镜头列表</h5>
          <div className="space-y-3">
            {data.shots.slice(0, 5).map((shot: any, idx: number) => (
              <div key={idx} className="text-xs border-l-2 border-muted pl-2">
                <div className="font-medium">镜头 {shot.shot_number} <span className="text-muted-foreground">| 场景 {shot.scene_ref}</span></div>
                <div className="text-muted-foreground mt-1">角度: {shot.camera_angle} | 运镜: {shot.camera_movement}</div>
                <div className="text-muted-foreground mt-1">时长: {shot.duration_sec}秒</div>
                <div className="text-muted-foreground mt-1">描述: {shot.description}</div>
                <div className="text-muted-foreground mt-1">图像提示: {shot.image_prompt?.slice(0, 100)}...</div>
              </div>
            ))}
            {data.shots.length > 5 && (
              <div className="text-xs text-muted-foreground text-center">... 还有 {data.shots.length - 5} 个镜头</div>
            )}
          </div>
        </div>
      )}
    </div>
  );

  const formatAudio = (data: any) => (
    <div className="space-y-4">
      {data.voice_cast && Object.keys(data.voice_cast).length > 0 && (
        <div>
          <h5 className="text-xs font-semibold mb-2 text-primary">配音阵容</h5>
          <div className="space-y-2">
            {Object.entries(data.voice_cast).map(([char, voice]: [string, any], idx: number) => (
              <div key={idx} className="text-xs border-l-2 border-muted pl-2">
                <div className="font-medium">{char}</div>
                <div className="text-muted-foreground">声音ID: {voice.voice_id} | 风格: {voice.voice_style}</div>
              </div>
            ))}
          </div>
        </div>
      )}
      {data.dialogue_plan && data.dialogue_plan.length > 0 && (
        <div>
          <h5 className="text-xs font-semibold mb-2 text-primary">对话计划</h5>
          <div className="space-y-2">
            {data.dialogue_plan.slice(0, 5).map((dialogue: any, idx: number) => (
              <div key={idx} className="text-xs border-l-2 border-muted pl-2">
                <div className="font-medium">{dialogue.character}: {dialogue.text?.slice(0, 50)}...</div>
                <div className="text-muted-foreground">场景 {dialogue.scene_ref} | 情绪: {dialogue.emotion} | 开始时间: {dialogue.start_sec}s</div>
              </div>
            ))}
            {data.dialogue_plan.length > 5 && (
              <div className="text-xs text-muted-foreground text-center">... 还有 {data.dialogue_plan.length - 5} 条对话</div>
            )}
          </div>
        </div>
      )}
      {data.bgm_plan && data.bgm_plan.length > 0 && (
        <div>
          <h5 className="text-xs font-semibold mb-2 text-primary">背景音乐</h5>
          <div className="space-y-2">
            {data.bgm_plan.slice(0, 3).map((bgm: any, idx: number) => (
              <div key={idx} className="text-xs border-l-2 border-muted pl-2">
                <div className="font-medium">场景 {bgm.scene_ref}</div>
                <div className="text-muted-foreground">风格: {bgm.style} | 情绪: {bgm.mood} | 时长: {bgm.duration_sec}s</div>
              </div>
            ))}
          </div>
        </div>
      )}
      {data.sfx_plan && data.sfx_plan.length > 0 && (
        <div>
          <h5 className="text-xs font-semibold mb-2 text-primary">音效计划</h5>
          <div className="space-y-2">
            {data.sfx_plan.slice(0, 3).map((sfx: any, idx: number) => (
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

  return (
    <div className="overflow-auto max-h-96">
      {formatContent()}
    </div>
  );
}