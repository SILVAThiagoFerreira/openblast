from __future__ import annotations

import json

from src.config_loader import load_config
from src.data_reader import read_workbook
from src.output_writer import write_manifest, write_summary
from src.processor import build_manifest, build_summary, build_tool_records, make_timestamp
from src.validator import validate_inputs


def test_output_writer_persists_json(temp_workspace):
    config = load_config(temp_workspace["config_path"])
    workbook = read_workbook(
        temp_workspace["input_workbook"],
        config["workbook"]["sheet_name"],
        config["workbook"]["header_row"],
    )
    report = validate_inputs(config, workbook)
    records = build_tool_records(config, workbook)
    run_id = "20260525_120000"
    generated_at = make_timestamp(config)
    manifest = build_manifest(config, workbook, records, run_id, generated_at)
    summary = build_summary(
        config,
        workbook,
        report,
        run_id,
        generated_at,
        status="success",
        stage="complete",
        message="Pipeline completed successfully",
        manifest_path=str(temp_workspace["output_dir"] / "usvaleverde" / "tools_manifest.json"),
        summary_path=str(temp_workspace["output_dir"] / "run_summary_20260525_120000.json"),
        log_path=str(temp_workspace["logs_dir"] / "pipeline_20260525_120000.log"),
    )

    manifest_path = write_manifest(
        manifest,
        temp_workspace["output_dir"] / "usvaleverde" / "tools_manifest.json",
        config["output"],
    )
    summary_path = write_summary(summary, temp_workspace["output_dir"] / "run_summary_20260525_120000.json", config["output"])

    assert manifest_path.exists()
    assert summary_path.exists()

    manifest_payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    summary_payload = json.loads(summary_path.read_text(encoding="utf-8"))

    assert manifest_payload["tools"]
    assert summary_payload["status"] == "success"
