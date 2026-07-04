"""Scan result models."""

from typing import Any

from pydantic import BaseModel, Field


class PluginResult(BaseModel):
    """Structured result returned by a plugin."""

    name: str
    detected: bool = False
    technologies: list[str] = Field(default_factory=list)
    findings: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    data: dict[str, Any] = Field(default_factory=dict)


class ScanResult(BaseModel):
    """Result produced after scanning a repository."""

    project_name: str
    project_code: str
    generated_at: str
    root_path: str
    files_scanned: int
    directories_scanned: int
    plugins: list[PluginResult] = Field(default_factory=list)
    technologies: list[str] = Field(default_factory=list)
    findings: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)

