"""Carregamento e normalizacao da configuracao externa."""

from __future__ import annotations

from copy import deepcopy
import json
import re
from pathlib import Path

from .exceptions import ConfigError


REQUIRED_TOP_LEVEL_KEYS = (
    "project",
    "paths",
    "workbook",
    "validation",
    "artifacts",
    "output",
    "runtime",
    "tool_metadata",
)

REQUIRED_TOOL_METADATA_KEYS = ("description", "kind", "accent", "accent2")
HEX_COLOR_PATTERN = re.compile(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")


def load_config(config_path: str | Path) -> dict:
    config_file = Path(config_path).expanduser().resolve()
    if not config_file.exists():
        raise ConfigError(f"Config file not found: {config_file}")

    try:
        with config_file.open("r", encoding="utf-8") as handle:
            raw_config = json.load(handle)
    except json.JSONDecodeError as exc:
        raise ConfigError(f"Invalid JSON in config file {config_file}: {exc}") from exc

    if not isinstance(raw_config, dict):
        raise ConfigError("Config root must be a JSON object")

    config = deepcopy(raw_config)
    _validate_top_level(config)
    _validate_sections(config)

    project_root = config_file.parent
    paths = config["paths"]
    artifacts = config["artifacts"]

    config["config_path"] = config_file
    config["project_root"] = project_root
    config["resolved_paths"] = {
        "input_workbook": (project_root / paths["input_workbook"]).resolve(),
        "output_directory": (project_root / paths["output_directory"]).resolve(),
        "logs_directory": (project_root / paths["logs_directory"]).resolve(),
        "manifest_file": (project_root / paths["output_directory"] / artifacts["manifest_filename"]).resolve(),
    }

    return config


def build_runtime_paths(config: dict, run_id: str) -> dict:
    output_directory = Path(config["resolved_paths"]["output_directory"])
    logs_directory = Path(config["resolved_paths"]["logs_directory"])
    artifacts = config["artifacts"]

    return {
        "input_workbook": Path(config["resolved_paths"]["input_workbook"]),
        "output_directory": output_directory,
        "logs_directory": logs_directory,
        "manifest_file": Path(config["resolved_paths"]["manifest_file"]),
        "summary_file": output_directory / artifacts["summary_filename_pattern"].format(run_id=run_id),
        "log_file": logs_directory / artifacts["log_filename_pattern"].format(run_id=run_id),
    }


def ensure_runtime_directories(runtime_paths: dict) -> None:
    runtime_paths["output_directory"].mkdir(parents=True, exist_ok=True)
    runtime_paths["logs_directory"].mkdir(parents=True, exist_ok=True)


def _validate_top_level(config: dict) -> None:
    missing = [key for key in REQUIRED_TOP_LEVEL_KEYS if key not in config]
    if missing:
        raise ConfigError(f"Missing required config sections: {', '.join(missing)}")


def _validate_sections(config: dict) -> None:
    _require_mapping(config, "project")
    _require_mapping(config, "paths")
    _require_mapping(config, "workbook")
    _require_mapping(config, "validation")
    _require_mapping(config, "artifacts")
    _require_mapping(config, "output")
    _require_mapping(config, "runtime")
    _require_mapping(config, "tool_metadata")

    _require_string(config["project"], "name")
    _require_string(config["project"], "version")
    _require_string(config["project"], "purpose")

    for key in ("input_workbook", "output_directory", "logs_directory"):
        _require_string(config["paths"], key)

    _require_string(config["workbook"], "sheet_name")
    _require_int(config["workbook"], "header_row")
    _require_non_empty_list(config["workbook"], "required_columns")

    validation = config["validation"]
    _require_string(validation, "allowed_scheme")
    _require_string(validation, "github_host_suffix")
    _require_string(validation, "pages_host_suffix")
    _require_string(validation, "repository_id_pattern")
    _require_int(validation, "min_rows")
    _require_int(validation, "max_rows")
    _require_bool(validation, "ignore_extra_columns")
    _require_bool(validation, "require_tool_metadata")
    if validation["require_tool_metadata"] is not True:
        raise ConfigError("validation.require_tool_metadata must remain true for this pipeline")

    artifacts = config["artifacts"]
    _require_string(artifacts, "manifest_filename")
    _require_string(artifacts, "summary_filename_pattern")
    _require_string(artifacts, "log_filename_pattern")

    output = config["output"]
    _require_int(output, "indent")
    _require_bool(output, "ensure_ascii")

    runtime = config["runtime"]
    _require_string(runtime, "timestamp_format")
    _require_string(runtime, "run_id_format")

    tool_metadata = config["tool_metadata"]
    if not tool_metadata:
        raise ConfigError("tool_metadata cannot be empty")

    for tool_id, metadata in tool_metadata.items():
        if not isinstance(metadata, dict):
            raise ConfigError(f"tool_metadata entry for '{tool_id}' must be an object")
        for field_name in REQUIRED_TOOL_METADATA_KEYS:
            _require_string(metadata, field_name)
        for color_field in ("accent", "accent2"):
            if not HEX_COLOR_PATTERN.match(metadata[color_field]):
                raise ConfigError(
                    f"tool_metadata entry for '{tool_id}' has invalid {color_field}: {metadata[color_field]}"
                )


def _require_mapping(container: dict, key: str) -> None:
    value = container.get(key)
    if not isinstance(value, dict):
        raise ConfigError(f"Config section '{key}' must be an object")


def _require_string(container: dict, key: str) -> None:
    value = container.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ConfigError(f"Config field '{key}' must be a non-empty string")


def _require_int(container: dict, key: str) -> None:
    value = container.get(key)
    if not isinstance(value, int):
        raise ConfigError(f"Config field '{key}' must be an integer")


def _require_bool(container: dict, key: str) -> None:
    value = container.get(key)
    if not isinstance(value, bool):
        raise ConfigError(f"Config field '{key}' must be a boolean")


def _require_non_empty_list(container: dict, key: str) -> None:
    value = container.get(key)
    if not isinstance(value, list) or not value:
        raise ConfigError(f"Config field '{key}' must be a non-empty list")
