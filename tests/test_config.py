from pathlib import Path

from docucore.core.config import (
    build_default_config,
    initialize_project,
    load_project_config,
    resolve_runtime_context,
)


def test_config_can_be_created_and_loaded_for_external_output(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    documentation_root = tmp_path / "workspace" / "docs"
    project_root.mkdir(parents=True)

    initialize_project(
        project_root,
        documentation_root,
        project_name="Demo Project",
        project_code="DEMO",
    )

    config = load_project_config(documentation_root / "config" / "project.config.json")

    assert config.project_name == "Demo Project"
    assert config.project_code == "DEMO"
    assert config.root_path == project_root.resolve().as_posix()
    assert config.documentation_path == documentation_root.resolve().as_posix()


def test_init_creates_documentation_structure_in_output_root(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    documentation_root = tmp_path / "workspace" / "docs"
    project_root.mkdir(parents=True)

    result = initialize_project(project_root, documentation_root)

    assert (documentation_root / "config" / "project.config.json").exists()
    assert (documentation_root / "outputs" / "inventory").exists()
    assert (documentation_root / "historical").exists()
    assert result["created_directories"]


def test_default_config_contains_expected_plugins() -> None:
    config = build_default_config()

    assert config.enabled_plugins == ["generic", "python", "node", "dotnet", "docker"]


def test_runtime_context_keeps_backward_compatibility_without_explicit_paths(
    tmp_path: Path,
    monkeypatch,
) -> None:
    initialize_project(tmp_path, tmp_path / "documentacion")
    monkeypatch.chdir(tmp_path)

    context = resolve_runtime_context(require_config=True)

    assert context.project_root == tmp_path.resolve()
    assert context.documentation_root == (tmp_path / "documentacion").resolve()
