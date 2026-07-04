"""Manifest models."""

from pydantic import BaseModel, Field


class Manifest(BaseModel):
    """Manifest generated for latest and historical snapshots."""

    project_name: str
    project_code: str
    generated_at: str
    docucore_version: str
    snapshot_id: str
    outputs: list[str] = Field(default_factory=list)
    plugins: list[str] = Field(default_factory=list)

