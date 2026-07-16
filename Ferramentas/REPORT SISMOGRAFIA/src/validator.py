from __future__ import annotations

import math
import re
from typing import Any, Dict, Iterable, List

from .exceptions import ConfigurationError, ValidationError


REQUIRED_CONFIG_SECTIONS = ("project", "paths", "output", "logging", "limits", "charts", "artifacts", "processing")
REQUIRED_RECORD_FIELDS = ("source_file", "event_date", "point_name", "pspl_db", "pvs_mm_s", "tran_ppv_mm_s", "vert_ppv_mm_s", "long_ppv_mm_s")
OPTIONAL_NUMERIC_FIELDS = ("gps_distance_m", "scaled_distance", "charge_kg", "mic_freq_hz", "tran_freq_hz", "vert_freq_hz", "long_freq_hz")
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _ensure_non_empty_string(value: Any, label: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ConfigurationError(f"Missing or invalid configuration value: {label}")


def _ensure_numeric(value: Any, label: str, allow_none: bool = False) -> None:
    if value is None and allow_none:
        return
    if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(float(value)):
        raise ConfigurationError(f"Invalid numeric configuration value: {label}")


def validate_config(config: Dict) -> Dict:
    if not isinstance(config, dict):
        raise ConfigurationError("Configuration must be a dictionary.")

    for section in REQUIRED_CONFIG_SECTIONS:
        if section not in config or not isinstance(config[section], dict):
            raise ConfigurationError(f"Missing configuration section: {section}")

    paths = config["paths"]
    _ensure_non_empty_string(paths.get("input_dir"), "paths.input_dir")
    _ensure_non_empty_string(paths.get("output_root"), "paths.output_root")
    _ensure_non_empty_string(paths.get("logs_root"), "paths.logs_root")

    output_cfg = config["output"]
    _ensure_non_empty_string(output_cfg.get("folder_prefix"), "output.folder_prefix")
    _ensure_non_empty_string(output_cfg.get("file_prefix"), "output.file_prefix")
    _ensure_non_empty_string(output_cfg.get("run_folder_template"), "output.run_folder_template")

    logging_cfg = config["logging"]
    _ensure_non_empty_string(logging_cfg.get("level"), "logging.level")
    _ensure_non_empty_string(logging_cfg.get("file_template"), "logging.file_template")

    artifacts = config["artifacts"]
    for key in ("report_pdf", "report_png", "whatsapp_note", "data_json", "manifest_json", "pressure_chart", "vibration_chart"):
        _ensure_non_empty_string(artifacts.get(key), f"artifacts.{key}")

    limits = config["limits"]
    _ensure_numeric(limits.get("sound_pressure_db"), "limits.sound_pressure_db")
    _ensure_numeric(limits.get("vibration_status_mm_s"), "limits.vibration_status_mm_s")
    curve = limits.get("nbr9653_curve")
    if not isinstance(curve, list) or not curve:
        raise ConfigurationError("limits.nbr9653_curve must be a non-empty list.")
    for idx, point in enumerate(curve, 1):
        if not isinstance(point, list) or len(point) != 2:
            raise ConfigurationError(f"limits.nbr9653_curve[{idx}] must contain exactly two numbers.")
        _ensure_numeric(point[0], f"limits.nbr9653_curve[{idx}][0]")
        _ensure_numeric(point[1], f"limits.nbr9653_curve[{idx}][1]")

    charts = config["charts"]
    for key in ("vibration_x_min", "vibration_y_min", "vibration_y_tick_step", "vibration_y_focus_max", "vibration_x_max_minimum", "vibration_y_max_minimum", "pressure_x_min", "pressure_y_min", "pressure_y_max"):
        _ensure_numeric(charts.get(key), f"charts.{key}")

    processing = config["processing"]
    if not isinstance(processing.get("require_single_event_date"), bool):
        raise ConfigurationError("processing.require_single_event_date must be boolean.")
    if not isinstance(processing.get("allow_missing_optional_fields"), bool):
        raise ConfigurationError("processing.allow_missing_optional_fields must be boolean.")

    return config


def _ensure_record_numeric(record: Dict, field: str, allow_none: bool = False) -> None:
    value = record.get(field)
    if value is None and allow_none:
        return
    if value is None:
        raise ValidationError(f"Missing required numeric field: {field}")
    if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(float(value)):
        raise ValidationError(f"Invalid numeric field: {field}")
    if float(value) < 0:
        raise ValidationError(f"Negative numeric value not allowed: {field}")


def validate_input_records(records: List[Dict], config: Dict) -> List[Dict]:
    if not records:
        raise ValidationError("No input records were found.")

    event_dates = set()
    for index, record in enumerate(records, 1):
        if not isinstance(record, dict):
            raise ValidationError(f"Record {index} must be a dictionary.")
        for field in REQUIRED_RECORD_FIELDS:
            if record.get(field) in (None, ""):
                raise ValidationError(f"Record {index} is missing required field: {field}")
        if not DATE_PATTERN.match(str(record["event_date"])):
            raise ValidationError(f"Record {index} has invalid event_date format: {record['event_date']}")
        event_dates.add(record["event_date"])
        for field in ("pspl_db", "pvs_mm_s", "tran_ppv_mm_s", "vert_ppv_mm_s", "long_ppv_mm_s"):
            _ensure_record_numeric(record, field)
        for field in OPTIONAL_NUMERIC_FIELDS:
            _ensure_record_numeric(record, field, allow_none=True)

    if config.get("processing", {}).get("require_single_event_date", True) and len(event_dates) > 1:
        raise ValidationError(f"Multiple event dates found in a single run: {sorted(event_dates)}")

    return records


def validate_processed_results(records: List[Dict], summary: Dict, config: Dict) -> Dict:
    if not isinstance(summary, dict):
        raise ValidationError("Processed summary must be a dictionary.")
    if summary.get("points_count") != len(records):
        raise ValidationError("Summary points_count does not match number of records.")
    if not summary.get("event_date"):
        raise ValidationError("Processed summary is missing the event_date.")
    if not summary.get("client"):
        raise ValidationError("Processed summary is missing the client.")
    return summary
