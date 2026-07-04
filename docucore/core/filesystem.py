"""Filesystem helpers for DocuCore."""

from __future__ import annotations

import json
import os
import shutil
from collections.abc import Iterable, Sequence
from pathlib import Path

from docucore.core.constants import DOCUMENTATION_SUBDIRECTORIES


def create_directory(path: Path) -> bool:
    """Create a directory and report whether it was newly created."""

    existed = path.exists()
    path.mkdir(parents=True, exist_ok=True)
    return not existed


def documentation_paths(documentation_root: Path) -> dict[str, Path]:
    """Return the standard documentation directory structure for a project."""

    doc_root = documentation_root.resolve()
    config_dir = doc_root / "config"
    outputs_dir = doc_root / "outputs"
    return {
        "documentation_root": doc_root,
        "config_dir": config_dir,
        "config_path": config_dir / "project.config.json",
        "outputs_dir": outputs_dir,
        "inventory_dir": outputs_dir / "inventory",
        "traceability_dir": outputs_dir / "traceability",
        "audits_dir": outputs_dir / "audits",
        "integral_dir": outputs_dir / "integral",
        "final_dir": outputs_dir / "final",
        "historical_dir": doc_root / "historical",
        "latest_dir": doc_root / "latest",
        "sources_dir": doc_root / "sources",
        "manual_inputs_dir": doc_root / "sources" / "optional_manual_inputs",
    }


def ensure_documentation_structure(documentation_root: Path) -> list[Path]:
    """Create the standard documentation structure and return created directories."""

    created: list[Path] = []
    doc_root = documentation_root.resolve()
    for relative_dir in DOCUMENTATION_SUBDIRECTORIES:
        path = doc_root / relative_dir
        if create_directory(path):
            created.append(path)
    return created


def write_json(path: Path, data: object) -> None:
    """Write JSON data with stable formatting."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False, sort_keys=False),
        encoding="utf-8",
    )


def read_json(path: Path) -> object:
    """Read JSON data from disk."""

    return json.loads(path.read_text(encoding="utf-8"))


def write_text(path: Path, content: str) -> None:
    """Write UTF-8 text content to disk."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def copy_file(source: Path, destination: Path) -> None:
    """Copy a file preserving metadata when possible."""

    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def _normalize_pattern(pattern: str) -> str:
    return pattern.replace("\\", "/").strip("/")


def relative_path_from(base_path: Path, target_path: Path) -> Path | None:
    """Return target relative to base when target is nested inside base."""

    try:
        return target_path.resolve().relative_to(base_path.resolve())
    except ValueError:
        return None


def is_excluded(relative_path: Path, exclude_patterns: Sequence[str]) -> bool:
    """Return True when a relative path matches an exclusion rule."""

    normalized = relative_path.as_posix()
    if normalized == ".":
        return False
    if normalized.startswith("./"):
        normalized = normalized[2:]

    parts = Path(normalized).parts
    for raw_pattern in exclude_patterns:
        pattern = _normalize_pattern(raw_pattern)
        if not pattern:
            continue
        if "/" in pattern:
            if normalized == pattern or normalized.startswith(f"{pattern}/"):
                return True
            continue
        if pattern in parts:
            return True
    return False


def iter_project_files(
    root: Path,
    include_paths: Iterable[str],
    exclude_paths: Sequence[str],
    documentation_root: Path | None = None,
) -> tuple[list[Path], set[Path]]:
    """Iterate files in a project while respecting include and exclude rules."""

    all_files: list[Path] = []
    directories: set[Path] = set()
    effective_excludes = list(exclude_paths)
    if documentation_root is not None:
        documentation_relative = relative_path_from(root, documentation_root)
        if documentation_relative not in {None, Path(".")}:
            effective_excludes.append(documentation_relative.as_posix())

    for include_path in include_paths:
        base_path = (root / include_path).resolve()
        if not base_path.exists():
            continue
        if base_path.is_file():
            relative_file = base_path.relative_to(root)
            if not is_excluded(relative_file, effective_excludes):
                all_files.append(relative_file)
            continue

        for current_root, dirnames, filenames in os.walk(base_path):
            current_path = Path(current_root)
            relative_dir = current_path.relative_to(root)
            dirnames[:] = [
                dirname
                for dirname in dirnames
                if not is_excluded(relative_dir / dirname, effective_excludes)
            ]
            if relative_dir != Path("."):
                directories.add(relative_dir)
            for filename in filenames:
                relative_file = (current_path / filename).relative_to(root)
                if not is_excluded(relative_file, effective_excludes):
                    all_files.append(relative_file)

    unique_files = sorted(set(all_files))
    return unique_files, directories


def list_snapshot_directories(historical_dir: Path) -> list[Path]:
    """List historical snapshot directories sorted by newest identifier first."""

    if not historical_dir.exists():
        return []
    return sorted((path for path in historical_dir.iterdir() if path.is_dir()), reverse=True)
