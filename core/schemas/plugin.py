"""NetverseIQ — Plugin Pydantic schemas"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Any, Dict, List


class MenuItem(BaseModel):
    label: str
    icon: str = "Puzzle"
    path: str
    permissions: List[str] = []


class PluginOut(BaseModel):
    id: int
    plugin_id: str
    name: str
    version: str
    description: str
    author: str
    is_enabled: bool
    manifest: Dict[str, Any]
    installed_at: datetime
    model_config = {"from_attributes": True}


class PluginToggle(BaseModel):
    is_enabled: bool
