from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from .parser import parse_many


def read_input_records(input_path: str | Path, logger=None) -> List[Dict]:
    records = [record.to_dict() for record in parse_many(input_path)]
    if logger:
        logger.info("Loaded %d record(s) from %s", len(records), input_path)
    return records
