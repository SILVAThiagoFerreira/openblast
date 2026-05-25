from __future__ import annotations

import json
import shutil
from copy import deepcopy
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def project_root() -> Path:
    return PROJECT_ROOT


@pytest.fixture(scope="session")
def base_config(project_root: Path) -> dict:
    config_path = project_root / "config.json"
    return json.loads(config_path.read_text(encoding="utf-8"))


@pytest.fixture()
def temp_workspace(tmp_path: Path, project_root: Path, base_config: dict) -> dict:
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    logs_dir = tmp_path / "logs"

    input_dir.mkdir()
    output_dir.mkdir()
    logs_dir.mkdir()

    shutil.copy2(
        project_root / "input" / "repositorios_github_pages.xlsx",
        input_dir / "repositorios_github_pages.xlsx",
    )

    config = deepcopy(base_config)
    config["paths"]["input_workbook"] = "input/repositorios_github_pages.xlsx"
    config["paths"]["output_directory"] = "output"
    config["paths"]["logs_directory"] = "logs"

    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")

    return {
        "root": tmp_path,
        "config_path": config_path,
        "input_workbook": input_dir / "repositorios_github_pages.xlsx",
        "output_dir": output_dir,
        "logs_dir": logs_dir,
    }
