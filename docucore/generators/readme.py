"""Small reusable text fragments for human-facing outputs."""

from __future__ import annotations

from docucore.models import ScanResult


def build_project_overview(scan_result: ScanResult) -> str:
    """Build a one-line overview for display surfaces."""

    technologies = (
        ", ".join(scan_result.technologies)
        if scan_result.technologies
        else "sin tecnologias detectadas"
    )
    return f"{scan_result.project_name} ({scan_result.project_code}) - {technologies}"
