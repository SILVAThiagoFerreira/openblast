from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List

from .artifacts import build_artifact_context, resolve_run_folder_name
from .config_loader import load_config as load_normalized_config


def load_config(path: str | Path) -> Dict[str, Any]:
    return load_normalized_config(path)


def save_json(data: Any, path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return path


def write_text(text: str, path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8')
    return path


def safe_slug(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r'[^a-z0-9_\-]+', '_', value)
    value = re.sub(r'_+', '_', value).strip('_')
    return value or 'saida'


def make_output_dir(config: Dict, records: List[Dict]) -> Path:
    paths_cfg = config.get("paths", {})
    root = Path(paths_cfg.get("output_root", config.get("output", {}).get("root", "output")))
    event_date = records[0].get("event_date") if records else None
    context = build_artifact_context(config, event_date=event_date)
    out = root / resolve_run_folder_name(config, context)
    out.mkdir(parents=True, exist_ok=True)
    return out


def output_file_stem(config: Dict, records: List[Dict]) -> str:
    prefix = config.get("output", {}).get("file_prefix", "ENAEX_NSR")
    event_date = None
    if records:
        event_date = records[0].get("event_date")
    date_part = event_date.replace('-', '') if event_date else datetime.now().strftime('%Y%m%d')
    return f"{prefix}-{date_part}"
