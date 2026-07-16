from __future__ import annotations

from pathlib import Path

from src.config_loader import load_config
from src.validator import validate_config


def test_config_loads_and_validates():
    config = load_config(Path("config.json"))
    validate_config(config)
    assert config["paths"]["output_root"] == "output"
    assert config["output"]["file_prefix"] == "ENAEX_NSR"
    assert "{file_prefix}" in config["artifacts"]["report_pdf"]
