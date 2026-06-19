from __future__ import annotations

import json

from main import main as run_main


def test_pipeline_end_to_end(temp_workspace):
    exit_code = run_main(["--config", str(temp_workspace["config_path"])])

    assert exit_code == 0

    manifest_path = temp_workspace["output_dir"] / "usvaleverde" / "tools_manifest.json"
    public_manifest_path = temp_workspace["output_dir"] / "public" / "tools_manifest.json"
    summary_files = list(temp_workspace["output_dir"].glob("run_summary_*.json"))
    log_files = list(temp_workspace["logs_dir"].glob("pipeline_*.log"))

    assert manifest_path.exists()
    assert public_manifest_path.exists()
    assert summary_files
    assert log_files
    assert (temp_workspace["public_dir"] / "index.html").exists()
    assert (temp_workspace["us_dir"] / "index.html").exists()

    manifest_payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    public_manifest_payload = json.loads(public_manifest_path.read_text(encoding="utf-8"))
    summary_payload = json.loads(summary_files[0].read_text(encoding="utf-8"))

    assert manifest_payload["project"]["name"] == "openblast"
    assert public_manifest_payload["project"]["name"] == "openblast"
    assert len(manifest_payload["tools"]) == 9
    assert len(manifest_payload["hubs"]) == 2
    assert manifest_payload["hubs"][0]["title"] == "Ferramentas Gerais"
    assert manifest_payload["hubs"][1]["title"] == "Ferramentas US Vale Verde"
    assert "tool_count" not in manifest_payload["hubs"][0]
    assert "tool_count" not in manifest_payload["hubs"][1]
    assert manifest_payload["publication"]["slug"] == "usvaleverde"
    assert public_manifest_payload["publication"]["slug"] == "public"
    assert len(public_manifest_payload["tools"]) == 6
    assert len(public_manifest_payload["hubs"]) == 1
    assert "tool_count" not in public_manifest_payload["hubs"][0]
    assert len(summary_payload["publish"]["targets"]) == 2
    assert [target["slug"] for target in summary_payload["publish"]["targets"]] == ["public", "usvaleverde"]
    assert summary_payload["paths"]["manifest"].replace("\\", "/").endswith("output/usvaleverde/tools_manifest.json")
    assert manifest_payload["source"]["sheet"] == "Repositorios"
