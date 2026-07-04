"""Base plugin contract."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from docucore.models import PluginResult


class BasePlugin(ABC):
    """Base class for all DocuCore plugins."""

    name = "base"

    @abstractmethod
    def detect(self, project_root: Path, files: list[Path]) -> dict[str, Any]:
        """Return light-weight detection metadata."""

    @abstractmethod
    def analyze(self, project_root: Path, files: list[Path]) -> PluginResult:
        """Return structured analysis data for this plugin."""

    def read_text(self, path: Path) -> str:
        """Read UTF-8 text safely."""

        return path.read_text(encoding="utf-8", errors="ignore")

