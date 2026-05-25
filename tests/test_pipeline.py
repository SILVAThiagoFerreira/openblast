from __future__ import annotations

import json

from main import main as run_main


def test_pipeline_end_to_end(temp_workspace):
    exit_code = run_main(["--config", str(temp_workspace["config_path"])])

    assert exit_code == 0

    manifest_path = temp_workspace["output_dir"] / "tools_manifest.json"
    summary_files = list(temp_workspace["output_dir"].glob("run_summary_*.json"))
    log_files = list(temp_workspace["logs_dir"].glob("pipeline_*.log"))

    assert manifest_path.exists()
    assert summary_files
    assert log_files

    manifest_payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert len(manifest_payload["tools"]) == 6
    assert manifest_payload["source"]["sheet"] == "Repositorios"
