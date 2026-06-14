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
    "publishing",
    "tool_metadata",
    "hubs",
)

REQUIRED_TOOL_METADATA_KEYS = ("description", "kind", "accent", "accent2")
REQUIRED_PUBLICATION_TARGET_KEYS = ("slug", "manifest_path", "html_path", "hub_slugs")
HEX_COLOR_PATTERN = re.compile(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")
PRIMARY_PUBLISHING_SLUG = "usvaleverde"
PUBLIC_PUBLISHING_SLUG = "public"


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
    resolved_publication_targets = _resolve_publication_targets(config, project_root)
    primary_target = _get_publication_target(resolved_publication_targets, PRIMARY_PUBLISHING_SLUG)

    config["config_path"] = config_file
    config["project_root"] = project_root
    config["resolved_publication_targets"] = resolved_publication_targets
    config["resolved_primary_publication_target"] = primary_target
    config["resolved_paths"] = {
        "input_workbook": (project_root / paths["input_workbook"]).resolve(),
        "output_directory": (project_root / paths["output_directory"]).resolve(),
        "logs_directory": (project_root / paths["logs_directory"]).resolve(),
        "manifest_file": primary_target["manifest_file"],
        "index_file": primary_target["html_file"],
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
        "index_file": Path(config["resolved_paths"]["index_file"]),
        "summary_file": output_directory / artifacts["summary_filename_pattern"].format(run_id=run_id),
        "log_file": logs_directory / artifacts["log_filename_pattern"].format(run_id=run_id),
        "publication_targets": config["resolved_publication_targets"],
    }


def ensure_runtime_directories(runtime_paths: dict) -> None:
    runtime_paths["output_directory"].mkdir(parents=True, exist_ok=True)
    runtime_paths["logs_directory"].mkdir(parents=True, exist_ok=True)

    for target in runtime_paths.get("publication_targets", []):
        Path(target["manifest_file"]).parent.mkdir(parents=True, exist_ok=True)
        Path(target["html_file"]).parent.mkdir(parents=True, exist_ok=True)


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
    _require_mapping(config, "publishing")
    _require_mapping(config, "tool_metadata")
    _require_mapping(config, "hubs")

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

    publishing = config["publishing"]
    _require_non_empty_list(publishing, "targets")

    target_slugs: set[str] = set()
    target_manifest_paths: set[str] = set()
    target_html_paths: set[str] = set()
    for target in publishing["targets"]:
        if not isinstance(target, dict):
            raise ConfigError("Each publishing target must be an object")
        for field_name in REQUIRED_PUBLICATION_TARGET_KEYS:
            if field_name not in target:
                raise ConfigError(f"Publishing target missing required field '{field_name}'")

        _require_string(target, "slug")
        _require_string(target, "manifest_path")
        _require_string(target, "html_path")
        _require_non_empty_list(target, "hub_slugs")

        if target["slug"] in target_slugs:
            raise ConfigError(f"Publishing target slug '{target['slug']}' is defined more than once")
        target_slugs.add(target["slug"])

        if target["manifest_path"] in target_manifest_paths:
            raise ConfigError(f"Publishing target manifest path '{target['manifest_path']}' is defined more than once")
        target_manifest_paths.add(target["manifest_path"])

        if target["html_path"] in target_html_paths:
            raise ConfigError(f"Publishing target html path '{target['html_path']}' is defined more than once")
        target_html_paths.add(target["html_path"])

        for hub_slug in target["hub_slugs"]:
            if not isinstance(hub_slug, str) or not hub_slug.strip():
                raise ConfigError(f"Publishing target '{target['slug']}' has an invalid hub slug")

    hubs = config["hubs"]
    _require_non_empty_list(hubs, "groups")
    all_group_ids: set[str] = set()
    all_group_slugs: set[str] = set()
    for group in hubs["groups"]:
        if not isinstance(group, dict):
            raise ConfigError("Each hub group must be an object")
        _require_string(group, "slug")
        _require_string(group, "title")
        _require_string(group, "description")
        _require_non_empty_list(group, "repository_ids")
        if group["slug"] in all_group_slugs:
            raise ConfigError(f"Hub group slug '{group['slug']}' is defined more than once")
        all_group_slugs.add(group["slug"])
        for repository_id in group["repository_ids"]:
            if not isinstance(repository_id, str) or not repository_id.strip():
                raise ConfigError(f"Hub group '{group['slug']}' has an invalid repository id")
            if repository_id in all_group_ids:
                raise ConfigError(f"Repository id '{repository_id}' is assigned to more than one hub group")
            all_group_ids.add(repository_id)

    for target in publishing["targets"]:
        missing_hub_slugs = [hub_slug for hub_slug in target["hub_slugs"] if hub_slug not in all_group_slugs]
        if missing_hub_slugs:
            raise ConfigError(
                f"Publishing target '{target['slug']}' references unknown hub group(s): {', '.join(missing_hub_slugs)}"
            )

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

    missing_grouped_tools = [tool_id for tool_id in tool_metadata if tool_id not in all_group_ids]
    if missing_grouped_tools:
        raise ConfigError(
            "Every tool_metadata entry must belong to exactly one hub group: "
            + ", ".join(sorted(missing_grouped_tools))
        )

    expected_target_paths = {
        PUBLIC_PUBLISHING_SLUG: (
            Path(config["paths"]["output_directory"]) / "public" / artifacts["manifest_filename"],
            Path("public/index.html"),
        ),
        PRIMARY_PUBLISHING_SLUG: (
            Path(config["paths"]["output_directory"]) / "usvaleverde" / artifacts["manifest_filename"],
            Path("usvaleverde/index.html"),
        ),
    }

    for target_slug, (expected_manifest, expected_html) in expected_target_paths.items():
        target = next((item for item in publishing["targets"] if item["slug"] == target_slug), None)
        if target is None:
            raise ConfigError(f"Publishing targets must include a '{target_slug}' target")

        if Path(target["manifest_path"]) != expected_manifest:
            raise ConfigError(
                f"The '{target_slug}' publishing target manifest path must match the configured output directory and filename"
            )

        if Path(target["html_path"]) != expected_html:
            raise ConfigError(
                f"The '{target_slug}' publishing target html_path must be '{expected_html.as_posix()}'"
            )


def _resolve_publication_targets(config: dict, project_root: Path) -> list[dict]:
    resolved_targets: list[dict] = []
    for target in config["publishing"]["targets"]:
        resolved_targets.append(
            {
                "slug": target["slug"],
                "manifest_file": (project_root / target["manifest_path"]).resolve(),
                "html_file": (project_root / target["html_path"]).resolve(),
                "hub_slugs": list(target["hub_slugs"]),
            }
        )
    return resolved_targets


def _get_publication_target(targets: list[dict], slug: str) -> dict:
    for target in targets:
        if target["slug"] == slug:
            return target
    raise ConfigError(f"Publishing target '{slug}' is missing")


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
