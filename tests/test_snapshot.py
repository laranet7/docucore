from pathlib import Path

from docucore.core.config import initialize_project, resolve_runtime_context
from docucore.core.scanner import scan_project
from docucore.core.snapshot import create_snapshot_from_outputs
from docucore.core.writer import write_inventory_outputs


def test_snapshot_creates_historical_directory_in_external_output(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    documentation_root = tmp_path / "workspace" / "docs"
    (project_root / "src").mkdir(parents=True)
    (project_root / "src" / "main.py").write_text("print('hello')\n", encoding="utf-8")

    initialize_project(project_root, documentation_root, project_name="Demo", project_code="DEMO")
    context = resolve_runtime_context(
        project=project_root,
        output=documentation_root,
        require_config=True,
    )
    assert context.config is not None

    artifacts = scan_project(context, context.config)
    write_inventory_outputs(context, context.config, artifacts)
    snapshot = create_snapshot_from_outputs(context, context.config)

    assert snapshot.historical_dir.exists()
    assert (snapshot.historical_dir / "inventory.json").exists()
    assert (snapshot.historical_dir / "manifest.json").exists()
    assert (documentation_root / "latest" / "snapshot.md").exists()
