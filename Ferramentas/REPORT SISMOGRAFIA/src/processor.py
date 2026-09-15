from __future__ import annotations

from typing import Dict, List

from .compliance import campaign_summary, evaluate_records
from .exceptions import ConfigurationError


def process_campaign(records: List[Dict], config: Dict, logger=None) -> Dict:
    evaluated = evaluate_records(records, config)
    order = config.get("processing", {}).get("record_order", "source_order")
    if order == "gps_distance_ascending":
        evaluated.sort(
            key=lambda record: (
                record.get("gps_distance_m") is None,
                record.get("gps_distance_m") if record.get("gps_distance_m") is not None else float("inf"),
                str(record.get("point_name", "")),
                str(record.get("source_file", "")),
            )
        )
    elif order != "source_order":
        raise ConfigurationError(f"Unsupported processing.record_order: {order}")
    summary = campaign_summary(evaluated, config)
    if logger:
        logger.info("Processed %d record(s) into campaign summary", len(evaluated))
    return {
        "records": evaluated,
        "summary": summary,
    }
