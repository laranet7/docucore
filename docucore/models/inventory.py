"""Inventory output models."""

from typing import Any

from pydantic import BaseModel, Field

from docucore.models.scan import PluginResult


class InventorySummary(BaseModel):
    """Summary section for the generated inventory."""

    total_files: int
    total_directories: int
    detected_plugins: int
    relevant_files: list[str] = Field(default_factory=list)


class Inventory(BaseModel):
    """Consolidated inventory data."""

    summary: InventorySummary
    technologies: list[str] = Field(default_factory=list)
    modules: list[dict[str, Any]] = Field(default_factory=list)
    files: list[str] = Field(default_factory=list)
    plugins: list[PluginResult] = Field(default_factory=list)
    findings: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)

