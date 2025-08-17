export type AspectMode = '16:9'|'9:16'|'1:1';
export interface ProjectMeta {
  name: string; fps: 24|25|30;
  color: 'Rec709'|'sRGB';
  aspect_mode: AspectMode;
  resolutions: { landscape: string; portrait: string };
  outputs: ('landscape'|'portrait')[];
}
export interface StageParams {
  vace?: { preset: 'pose'|'depth'|'line'; prompt: string; seed?: number };
  standin?: { ref: string; pose_guided?: boolean };
  tooncomposer?: {
    sketch_keys: string[]; color_keys: string[];
    detail_strength?: number; inbetween_density?: number;
  };
  multitalk?: { audio: string; style: 'semi-real'|'neutral' };
}
export interface Shot {
  id: string; in: string; out: string;
  stages: StageParams;
  active_video: string; // e.g., "tooncomposer:v1"
}
export interface Project { project: ProjectMeta; shots: Shot[]; }


