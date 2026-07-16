from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from src.artifacts import build_artifact_context, resolve_artifact_name
from src.config_loader import load_config
from src.data_reader import read_input_records
from src.io_utils import make_output_dir
from src.processor import process_campaign
from src.output_writer import write_campaign_outputs
from src.validator import validate_input_records


def test_output_writer_creates_artifacts(tmp_path):
    config = load_config("config.json")
    config = deepcopy(config)
    config["paths"]["output_root"] = str(tmp_path / "output")
    config["paths"]["logs_root"] = str(tmp_path / "logs")

    records = read_input_records(Path("examples/input"))
    validate_input_records(records, config)
    processed = process_campaign(records, config)
    out_dir = make_output_dir(config, processed["records"])
    manifest = write_campaign_outputs(processed["records"], processed["summary"], config, "examples/input", out_dir)

    context = build_artifact_context(config, event_date=processed["summary"]["event_date"])
    expected_files = [
        out_dir / resolve_artifact_name(config, "report_pdf", context),
        out_dir / resolve_artifact_name(config, "report_png", context),
        out_dir / resolve_artifact_name(config, "whatsapp_note", context),
        out_dir / resolve_artifact_name(config, "data_json", context),
        out_dir / resolve_artifact_name(config, "manifest_json", context),
    ]
    for path in expected_files:
        assert path.exists()
        assert path.stat().st_size > 0
    assert manifest["output_dir"] == str(out_dir)
