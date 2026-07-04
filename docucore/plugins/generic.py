"""Generic repository plugin."""

from __future__ import annotations

from collections import Counter
from pathlib import Path

from docucore.core.constants import RELEVANT_FILENAMES, RELEVANT_GLOBS
from docucore.models import PluginResult
from docucore.plugins.base import BasePlugin


class GenericPlugin(BasePlugin):
    """Generic repository structure detector."""

    name = "generic"

    def detect(self, project_root: Path, files: list[Path]) -> dict[str, object]:
        return {"detected": bool(files), "file_count": len(files)}

    def analyze(self, project_root: Path, files: list[Path]) -> PluginResult:
        extensions = Counter(path.suffix.lower() or "[no extension]" for path in files)
        main_directories = sorted({path.parts[0] for path in files if len(path.parts) > 1})
        github_workflow_files = sorted(
            path.as_posix()
            for path in files
            if path.as_posix().startswith(".github/workflows/")
        )
        gitlab_ci_files = sorted(
            path.as_posix()
            for path in files
            if path.name == ".gitlab-ci.yml"
        )
        relevant_files = sorted(
            {
                path.as_posix()
                for path in files
                if path.name in RELEVANT_FILENAMES
                or any(path.match(pattern) for pattern in RELEVANT_GLOBS)
                or path.as_posix() == ".github/workflows"
                or path.as_posix().startswith(".github/workflows/")
            }
        )
        findings = [
            f"Archivos analizados: {len(files)}.",
            f"Directorios principales detectados: {len(main_directories)}.",
            f"Extensiones detectadas: {len(extensions)}.",
        ]
        warnings = ["No se encontraron archivos para analizar."] if not files else []
        return PluginResult(
            name=self.name,
            detected=bool(files),
            findings=findings,
            warnings=warnings,
            data={
                "total_files": len(files),
                "main_directories": main_directories,
                "extensions": dict(sorted(extensions.items())),
                "github_workflow_files": github_workflow_files,
                "gitlab_ci_files": gitlab_ci_files,
                "relevant_files": relevant_files,
            },
        )
