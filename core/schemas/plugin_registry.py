from pydantic import BaseModel
from typing import Any

class PluginRegistrySchema(BaseModel):
    plugin_id: str
    name: str
    version: str
    description: str
    author: str
    is_enabled: bool
    manifest: dict[str, Any]

    class Config:
        from_attributes = True

class PluginRegistryUpdateSchema(BaseModel):
    is_enabled: bool
