from __future__ import annotations

from typing import Dict, List

from .compliance import campaign_summary, evaluate_records


def process_campaign(records: List[Dict], config: Dict, logger=None) -> Dict:
    evaluated = evaluate_records(records, config)
    summary = campaign_summary(evaluated, config)
    if logger:
        logger.info("Processed %d record(s) into campaign summary", len(evaluated))
    return {
        "records": evaluated,
        "summary": summary,
    }
