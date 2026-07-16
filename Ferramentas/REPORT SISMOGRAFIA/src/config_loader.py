from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict

from .exceptions import ConfigurationError


DEFAULT_CONFIG: Dict[str, Any] = {
    "project": {
        "title": "MONITORAMENTO SISMOGRÁFICO",
        "client_default": "US MINERAÇÃO VALE-VERDE",
        "base_normativa": "ABNT NBR 9653:2018",
        "footer_badge": "DNA  •  ENAEX",
        "client_override": "US MINERAÇÃO VALE-VERDE",
    },
    "paths": {
        "input_dir": "input",
        "output_root": "output",
        "logs_root": "logs",
    },
    "output": {
        "folder_prefix": "monitoramento_sismografico",
        "file_prefix": "ENAEX_NSR",
        "run_folder_template": "{date}_{time}_{folder_prefix}",
    },
    "logging": {
        "level": "INFO",
        "file_template": "{file_prefix}-{date}_{time}.log",
    },
    "artifacts": {
        "report_pdf": "{file_prefix}-{date}.pdf",
        "report_png": "{file_prefix}-{date}.png",
        "whatsapp_note": "{file_prefix}-{date}_nota_whatsapp.txt",
        "data_json": "{file_prefix}-{date}_dados_extraidos.json",
        "manifest_json": "{file_prefix}-{date}_manifest.json",
        "pressure_chart": "{file_prefix}-{date}_pressao_sonora_nbr.png",
        "vibration_chart": "{file_prefix}-{date}_vibracao_nbr_eixos_zero.png",
    },
    "limits": {
        "sound_pressure_db": 134.0,
        "vibration_status_mm_s": 0.8,
        "vibration_compliance_mode": "nbr9653_curve",
        "nbr9653_curve": [
            [0.0, 15.0],
            [4.0, 15.0],
            [15.0, 20.0],
            [40.0, 50.0],
            [1000.0, 50.0],
        ],
    },
    "charts": {
        "vibration_x_min": 0.0,
        "vibration_y_min": 0.0,
        "vibration_y_tick_step": 0.1,
        "vibration_use_broken_y": True,
        "vibration_y_focus_max": 1.0,
        "vibration_x_max_minimum": 60.0,
        "vibration_y_max_minimum": 60.0,
        "pressure_x_min": 0.0,
        "pressure_y_min": 0.0,
        "pressure_y_max": 160.0,
    },
    "processing": {
        "require_single_event_date": True,
        "allow_missing_optional_fields": True,
    },
}


def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    result = deepcopy(base)
    for key, value in override.items():
        if isinstance(result.get(key), dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def _apply_legacy_aliases(config: Dict[str, Any], raw: Dict[str, Any]) -> Dict[str, Any]:
    output_cfg = config.setdefault("output", {})
    paths_cfg = config.setdefault("paths", {})
    logging_cfg = config.setdefault("logging", {})

    legacy_output = raw.get("output", {})
    legacy_paths = raw.get("paths", {})
    if isinstance(legacy_output, dict):
        if "root" in legacy_output:
            paths_cfg["output_root"] = legacy_output["root"]
        if "folder_prefix" in legacy_output:
            output_cfg["folder_prefix"] = legacy_output["folder_prefix"]
        if "file_prefix" in legacy_output:
            output_cfg["file_prefix"] = legacy_output["file_prefix"]

    if isinstance(legacy_paths, dict):
        if "input_dir" in legacy_paths:
            paths_cfg["input_dir"] = legacy_paths["input_dir"]
        if "output_root" in legacy_paths:
            paths_cfg["output_root"] = legacy_paths["output_root"]
        if "logs_root" in legacy_paths:
            paths_cfg["logs_root"] = legacy_paths["logs_root"]

    if "input_dir" not in paths_cfg:
        paths_cfg["input_dir"] = "input"
    if "output_root" not in paths_cfg:
        paths_cfg["output_root"] = "output"
    if "logs_root" not in paths_cfg:
        paths_cfg["logs_root"] = "logs"

    if "file_prefix" not in output_cfg:
        output_cfg["file_prefix"] = "ENAEX_NSR"
    if "run_folder_template" not in output_cfg:
        output_cfg["run_folder_template"] = "{date}_{time}_{folder_prefix}"

    if "file_template" not in logging_cfg:
        logging_cfg["file_template"] = "{file_prefix}-{date}_{time}.log"
    if "level" not in logging_cfg:
        logging_cfg["level"] = "INFO"

    return config


def load_config(path: str | Path) -> Dict[str, Any]:
    path = Path(path)
    if not path.exists():
        raise ConfigurationError(f"Configuration file not found: {path}")
    try:
        with path.open("r", encoding="utf-8") as handle:
            raw = json.load(handle)
    except json.JSONDecodeError as exc:
        raise ConfigurationError(f"Invalid JSON configuration: {path}") from exc
    if not isinstance(raw, dict):
        raise ConfigurationError("Configuration root must be a JSON object.")
    config = _deep_merge(DEFAULT_CONFIG, raw)
    return _apply_legacy_aliases(config, raw)
