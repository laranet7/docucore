"""Configuration models for DocuCore."""

from pydantic import BaseModel, ConfigDict, Field


class AISettings(BaseModel):
    """Optional AI settings placeholder."""

    model_config = ConfigDict(extra="forbid")

    enabled: bool = False


class ProjectConfig(BaseModel):
    """Project-level configuration."""

    model_config = ConfigDict(extra="forbid")

    project_name: str = "Unnamed Project"
    project_code: str = "UNNAMED"
    language: str = "es"
    root_path: str = "."
    documentation_path: str = "documentacion"
    include_paths: list[str] = Field(default_factory=lambda: ["."])
    exclude_paths: list[str] = Field(default_factory=list)
    enabled_plugins: list[str] = Field(default_factory=list)
    outputs: list[str] = Field(default_factory=list)
    exporters: list[str] = Field(default_factory=list)
    ai: AISettings = Field(default_factory=AISettings)

