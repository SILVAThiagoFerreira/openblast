from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from src.config_loader import load_config
from src.data_reader import read_input_records
from src.validator import validate_input_records
from src.exceptions import ValidationError


def test_required_directories_exist():
    root = Path(".")
    for relative in ("src", "input", "output", "logs", "tests"):
        assert (root / relative).exists()


def test_input_validation_accepts_example_records():
    config = load_config("config.json")
    records = read_input_records(Path("examples/input"))
    assert validate_input_records(records, config) == records


def test_input_validation_rejects_missing_required_field():
    config = load_config("config.json")
    records = read_input_records(Path("examples/input"))
    bad_record = deepcopy(records[0])
    bad_record["point_name"] = ""
    with pytest.raises(ValidationError):
        validate_input_records([bad_record], config)
