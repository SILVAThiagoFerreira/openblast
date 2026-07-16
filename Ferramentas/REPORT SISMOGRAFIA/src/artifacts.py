from __future__ import annotations

from datetime import datetime
from typing import Dict, Optional


def build_artifact_context(config: Dict, event_date: Optional[str] = None, current_dt: Optional[datetime] = None) -> Dict[str, str]:
    now = current_dt or datetime.now()
    date_part = (event_date or now.strftime("%Y-%m-%d")).replace("-", "")
    output_cfg = config.get("output", {})
    return {
        "date": date_part,
        "time": now.strftime("%H%M%S"),
        "file_prefix": output_cfg.get("file_prefix", "ENAEX_NSR"),
        "folder_prefix": output_cfg.get("folder_prefix", "monitoramento_sismografico"),
    }


def resolve_artifact_name(config: Dict, key: str, context: Dict[str, str]) -> str:
    artifacts = config.get("artifacts", {})
    template = artifacts.get(key)
    if not template:
        raise KeyError(f"Artifact template not configured: {key}")
    return template.format(**context)


def resolve_run_folder_name(config: Dict, context: Dict[str, str]) -> str:
    output_cfg = config.get("output", {})
    template = output_cfg.get("run_folder_template", "{date}_{time}_{folder_prefix}")
    return template.format(**context)
