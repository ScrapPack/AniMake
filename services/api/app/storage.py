import json, os
from typing import Optional
from .models import Project, Shot

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__),"../../.."))
PROJECT_PATH = os.path.join(ROOT, "project.json")

def load_project() -> Project:
    if not os.path.exists(PROJECT_PATH):
        p = Project()
        save_project(p)
        return p
    with open(PROJECT_PATH,"r",encoding="utf-8") as f:
        data = json.load(f)
    return Project.model_validate(data)

def save_project(p: Project):
    with open(PROJECT_PATH,"w",encoding="utf-8") as f:
        json.dump(p.model_dump(by_alias=True, exclude_none=True), f, indent=2)


