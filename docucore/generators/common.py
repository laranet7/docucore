"""Common helpers for generators."""

from __future__ import annotations

from pathlib import Path

from docucore.core.scanner import ScanArtifacts


def get_plugin_data(scan_artifacts: ScanArtifacts, plugin_name: str) -> dict[str, object]:
    """Return plugin data by plugin name."""

    for plugin in scan_artifacts.scan_result.plugins:
        if plugin.name == plugin_name:
            return plugin.data
    return {}


def get_plugin_findings(scan_artifacts: ScanArtifacts, plugin_name: str) -> list[str]:
    """Return plugin findings by plugin name."""

    for plugin in scan_artifacts.scan_result.plugins:
        if plugin.name == plugin_name:
            return plugin.findings
    return []


def first_level_directories(files: list[str], base_path: str) -> list[str]:
    """Return first-level child directories found beneath a base path."""

    base = Path(base_path)
    children: set[str] = set()
    for file_path in files:
        path = Path(file_path)
        try:
            relative = path.relative_to(base)
        except ValueError:
            continue
        if len(relative.parts) > 1:
            children.add(relative.parts[0])
    return sorted(children)


def list_matching_files(
    files: list[str],
    prefixes: tuple[str, ...],
    suffixes: tuple[str, ...],
) -> list[str]:
    """Return files that live under one of the prefixes and match the suffix list."""

    matches: list[str] = []
    for file_path in files:
        normalized = file_path.replace("\\", "/")
        if prefixes and not any(normalized.startswith(prefix) for prefix in prefixes):
            continue
        if suffixes and not normalized.endswith(suffixes):
            continue
        matches.append(normalized)
    return sorted(matches)
