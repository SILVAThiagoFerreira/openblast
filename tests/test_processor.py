from __future__ import annotations

from src.config_loader import load_config
from src.data_reader import read_workbook
from src.processor import build_manifest, build_tool_records, make_timestamp
from src.validator import validate_inputs


def test_processor_builds_manifest(temp_workspace):
    config = load_config(temp_workspace["config_path"])
    workbook = read_workbook(
        temp_workspace["input_workbook"],
        config["workbook"]["sheet_name"],
        config["workbook"]["header_row"],
    )
    report = validate_inputs(config, workbook)
    assert report.is_valid

    records = build_tool_records(config, workbook)
    generated_at = make_timestamp(config)
    manifest = build_manifest(config, workbook, records, "20260525_120000", generated_at)

    assert len(records) == 6
    assert manifest["counts"]["valid_rows"] == 6
    assert manifest["tools"][0]["repository_id"] == "enaex-plano-de-voo"
    assert manifest["tools"][0]["kind"] == "flight"
