from pydantic import BaseModel, Field
from typing import Literal, List, Optional, Dict

AspectMode = Literal['16:9','9:16','1:1']

class ProjectMeta(BaseModel):
    name: str = "AnimeFeature"
    fps: Literal[24,25,30] = 24
    color: Literal['Rec709','sRGB'] = 'Rec709'
    aspect_mode: AspectMode = '16:9'
    resolutions: Dict[str,str] = {"landscape":"1920x1080","portrait":"1080x1920"}
    outputs: List[Literal['landscape','portrait']] = ['landscape']

class VaceParams(BaseModel):
    preset: Literal['pose','depth','line'] = 'pose'
    prompt: str = ""
    seed: Optional[int] = None

class StandinParams(BaseModel):
    ref: str
    pose_guided: bool = True

class ToonParams(BaseModel):
    sketch_keys: List[str] = []
    color_keys: List[str] = []
    detail_strength: float = 0.7
    inbetween_density: float = 0.5

class MultiTalkParams(BaseModel):
    audio: str
    style: Literal['semi-real','neutral'] = 'semi-real'

class StageParams(BaseModel):
    vace: Optional[VaceParams] = None
    standin: Optional[StandinParams] = None
    tooncomposer: Optional[ToonParams] = None
    multitalk: Optional[MultiTalkParams] = None

class Shot(BaseModel):
    id: str
    in_: str = Field(alias="in")
    out: str
    stages: StageParams = StageParams()
    active_video: str = ""
    video_path: Optional[str] = None  # TEMP: raw video to proxy

class Project(BaseModel):
    project: ProjectMeta = ProjectMeta()
    shots: List[Shot] = []


