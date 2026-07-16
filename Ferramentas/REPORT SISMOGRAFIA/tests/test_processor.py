from __future__ import annotations

from pathlib import Path

from src.config_loader import load_config
from src.data_reader import read_input_records
from src.processor import process_campaign
from src.validator import validate_input_records, validate_processed_results


def test_processor_builds_campaign_summary():
    config = load_config("config.json")
    records = read_input_records(Path("examples/input"))
    validate_input_records(records, config)

    processed = process_campaign(records, config)
    validate_processed_results(processed["records"], processed["summary"], config)

    assert processed["summary"]["points_count"] == 2
    assert processed["summary"]["event_date"] == "2026-06-10"
    assert processed["summary"]["all_below_configured_vibration_limit"] is True
