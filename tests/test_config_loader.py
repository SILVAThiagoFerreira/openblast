from __future__ import annotations

from src.config_loader import build_runtime_paths, load_config


def test_load_config_normalizes_paths(project_root):
    config = load_config(project_root / "config.json")

    assert config["project"]["name"] == "hub-de-ferramentas-us-mvv"
    assert config["resolved_paths"]["input_workbook"].exists()
    assert config["resolved_paths"]["manifest_file"].name == "tools_manifest.json"
    assert len(config["tool_metadata"]) == 6


def test_build_runtime_paths_uses_run_id(project_root):
    config = load_config(project_root / "config.json")
    runtime_paths = build_runtime_paths(config, "20260525_120000")

    assert runtime_paths["summary_file"].name == "run_summary_20260525_120000.json"
    assert runtime_paths["log_file"].name == "pipeline_20260525_120000.log"
