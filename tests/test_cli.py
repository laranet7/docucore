from pathlib import Path

from typer.testing import CliRunner

from docucore.cli import app


def test_cli_help() -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "DocuCore CLI" in result.stdout


def test_cli_init_with_external_output(tmp_path: Path, monkeypatch) -> None:
    runner = CliRunner()
    project_root = tmp_path / "project"
    documentation_root = tmp_path / "workspace" / "docs"
    project_root.mkdir(parents=True)
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(
        app,
        [
            "init",
            "--project",
            str(project_root),
            "--output",
            str(documentation_root),
            "--project-name",
            "Sample Project",
            "--project-code",
            "SAMPLE",
        ],
    )

    assert result.exit_code == 0
    assert (documentation_root / "config" / "project.config.json").exists()
    assert not (project_root / "documentacion").exists()


def test_cli_scan_build_and_status_with_external_output(tmp_path: Path, monkeypatch) -> None:
    runner = CliRunner()
    project_root = tmp_path / "project"
    documentation_root = tmp_path / "workspace" / "docs"
    (project_root / "src").mkdir(parents=True)
    (project_root / "src" / "app.py").write_text("from fastapi import FastAPI\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    init_result = runner.invoke(
        app,
        [
            "init",
            "--project",
            str(project_root),
            "--output",
            str(documentation_root),
            "--project-name",
            "Sample Project",
            "--project-code",
            "SAMPLE",
        ],
    )
    scan_result = runner.invoke(
        app,
        [
            "scan",
            "--project",
            str(project_root),
            "--output",
            str(documentation_root),
        ],
    )
    build_result = runner.invoke(
        app,
        [
            "build",
            "--project",
            str(project_root),
            "--output",
            str(documentation_root),
        ],
    )
    status_result = runner.invoke(
        app,
        [
            "status",
            "--project",
            str(project_root),
            "--output",
            str(documentation_root),
        ],
    )

    assert init_result.exit_code == 0
    assert scan_result.exit_code == 0
    assert build_result.exit_code == 0
    assert status_result.exit_code == 0
    assert (documentation_root / "outputs" / "inventory" / "inventory.json").exists()
    assert (documentation_root / "latest" / "manifest.json").exists()
    assert "Project root:" in status_result.stdout
    assert "Documentation path:" in status_result.stdout
    assert "Enabled plugins: generic, python, node, dotnet, docker" in status_result.stdout
    assert not (project_root / "documentacion").exists()


def test_cli_backward_compatibility_without_project_or_output(
    tmp_path: Path,
    monkeypatch,
) -> None:
    runner = CliRunner()
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "main.py").write_text("print('hello')\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    init_result = runner.invoke(app, ["init", "--project-name", "Demo", "--project-code", "DEMO"])
    build_result = runner.invoke(app, ["build"])

    assert init_result.exit_code == 0
    assert build_result.exit_code == 0
    assert (tmp_path / "documentacion" / "latest" / "inventory.json").exists()
