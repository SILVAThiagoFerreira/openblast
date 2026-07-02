"""Processamento e enriquecimento dos dados validados."""

from __future__ import annotations

import platform
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

import openpyxl

from .exceptions import ProcessingError
from .models import ToolRecord, ValidationReport


def build_tool_records(config: dict, workbook_result) -> list[ToolRecord]:
    metadata = config["tool_metadata"]
    records: list[ToolRecord] = []

    for order, row in enumerate(workbook_result.rows, start=1):
        try:
            tool_meta = metadata[row.repository_id]
            github_owner, github_repo = _parse_github_url(row.github_url)
            pages_owner, pages_repo = _parse_pages_url(row.pages_url)
        except KeyError as exc:
            raise ProcessingError(f"Missing metadata for repository '{row.repository_id}'") from exc

        records.append(
            ToolRecord(
                row_number=row.row_number,
                repository_id=row.repository_id,
                formal_title=row.formal_title,
                github_url=row.github_url,
                pages_url=row.pages_url,
                description=tool_meta["description"],
                kind=tool_meta["kind"],
                accent=tool_meta["accent"],
                accent2=tool_meta["accent2"],
                github_owner=github_owner,
                github_repo_name=github_repo,
                pages_owner=pages_owner,
                pages_repo_name=pages_repo,
                order=order,
            )
        )

    return records


def build_hub_groups(config: dict, tool_records: list[ToolRecord]) -> list[dict]:
    records_by_id = {record.repository_id: record for record in tool_records}
    groups: list[dict] = []

    for group_config in config["hubs"]["groups"]:
        records = []
        for repository_id in group_config["repository_ids"]:
            try:
                records.append(asdict(records_by_id[repository_id]))
            except KeyError as exc:
                raise ProcessingError(
                    f"Missing tool record for repository '{repository_id}' in hub '{group_config['slug']}'"
                ) from exc

        groups.append(
            {
                "slug": group_config["slug"],
                "title": group_config["title"],
                "description": group_config["description"],
                "tools": records,
            }
        )

    return groups


def build_manifest(
    config: dict,
    workbook_result,
    tool_records: list[ToolRecord],
    run_id: str,
    generated_at: str,
    publication_target: dict | None = None,
) -> dict:
    all_hub_groups = build_hub_groups(config, tool_records)
    all_tools = [asdict(record) for record in tool_records]
    primary_publication_slug = (
        config.get("resolved_primary_publication_target", {}).get("slug")
        or "usvaleverde"
    )

    if publication_target is None:
        hub_groups = all_hub_groups
        tool_payloads = all_tools
        publication_payload = {
            "slug": primary_publication_slug,
            "hub_slugs": [group["slug"] for group in all_hub_groups],
            "source_hub_count": len(all_hub_groups),
            "source_tool_count": len(all_tools),
            "published_hub_count": len(all_hub_groups),
            "published_tool_count": len(all_tools),
            "excluded_hub_slugs": [],
        }
    else:
        allowed_hub_slugs = set(publication_target["hub_slugs"])
        excluded_repository_ids = set(publication_target.get("excluded_repository_ids", []))
        hub_groups = []
        for group in all_hub_groups:
            if group["slug"] not in allowed_hub_slugs:
                continue

            filtered_tools = [
                tool
                for tool in group["tools"]
                if tool["repository_id"] not in excluded_repository_ids
            ]
            if filtered_tools:
                hub_groups.append(
                    {
                        "slug": group["slug"],
                        "title": group["title"],
                        "description": group["description"],
                        "tools": filtered_tools,
                    }
                )

        allowed_repository_ids = {tool["repository_id"] for group in hub_groups for tool in group["tools"]}
        tool_payloads = [tool for tool in all_tools if tool["repository_id"] in allowed_repository_ids]
        published_hub_slugs = [group["slug"] for group in hub_groups]
        published_hub_slug_set = set(published_hub_slugs)
        publication_payload = {
            "slug": publication_target["slug"],
            "hub_slugs": published_hub_slugs,
            "source_hub_count": len(all_hub_groups),
            "source_tool_count": len(all_tools),
            "published_hub_count": len(hub_groups),
            "published_tool_count": len(tool_payloads),
            "excluded_hub_slugs": [group["slug"] for group in all_hub_groups if group["slug"] not in published_hub_slug_set],
        }

    return {
        "manifest_version": "2.0",
        "project": {
            "name": config["project"]["name"],
            "version": config["project"]["version"],
            "purpose": config["project"]["purpose"],
        },
        "generated_at": generated_at,
        "run_id": run_id,
        "source": {
            "workbook": str(config["paths"]["input_workbook"]),
            "sheet": workbook_result.sheet_name,
            "headers": workbook_result.headers,
            "sha256": workbook_result.source_hash,
            "row_count": len(workbook_result.rows),
        },
        "counts": {
            "total_rows": len(tool_payloads),
            "valid_rows": len(tool_payloads),
            "invalid_rows": 0,
            "hub_count": len(hub_groups),
        },
        "validation": {
            "status": "passed",
            "error_count": 0,
            "warning_count": 0,
        },
        "publication": publication_payload,
        "generator": {
            "python": platform.python_version(),
            "openpyxl": openpyxl.__version__,
        },
        "hubs": hub_groups,
        "tools": tool_payloads,
    }


def build_summary(
    config: dict,
    workbook_result,
    validation_report: ValidationReport | None,
    run_id: str,
    generated_at: str,
    status: str,
    stage: str,
    message: str,
    manifest_path: str | None,
    summary_path: str,
    log_path: str,
    published_targets: list[dict] | None = None,
) -> dict:
    validation_payload = validation_report.to_dict() if validation_report is not None else {
        "row_count": len(workbook_result.rows) if workbook_result is not None else 0,
        "error_count": 0,
        "warning_count": 0,
        "is_valid": status == "success",
        "issues": [],
    }

    row_count = len(workbook_result.rows) if workbook_result is not None else 0
    invalid_rows = 0
    if validation_report is not None:
        invalid_rows = len(
            {
                issue.row_number
                for issue in validation_report.issues
                if issue.severity == "error" and issue.row_number is not None
            }
        )
    elif status != "success":
        invalid_rows = row_count

    valid_count = row_count - invalid_rows if status != "success" else row_count
    invalid_count = invalid_rows

    return {
        "run_id": run_id,
        "status": status,
        "stage": stage,
        "message": message,
        "generated_at": generated_at,
        "paths": {
            "config": str(config["config_path"]),
            "input_workbook": str(config["resolved_paths"]["input_workbook"]),
            "output_directory": str(config["resolved_paths"]["output_directory"]),
            "logs_directory": str(config["resolved_paths"]["logs_directory"]),
            "manifest": manifest_path,
            "summary": summary_path,
            "log": log_path,
        },
        "source": {
            "workbook": str(config["paths"]["input_workbook"]),
            "sheet": workbook_result.sheet_name if workbook_result is not None else config["workbook"]["sheet_name"],
            "row_count": row_count,
        },
        "validation": validation_payload,
        "counts": {
            "total_rows": row_count,
            "valid_rows": valid_count,
            "invalid_rows": invalid_count,
            "error_count": validation_payload["error_count"],
            "warning_count": validation_payload["warning_count"],
        },
        "publish": {
            "targets": published_targets or [],
        },
        "generator": {
            "python": platform.python_version(),
            "openpyxl": openpyxl.__version__,
        },
    }


def make_timestamp(config: dict) -> str:
    return datetime.now(timezone.utc).strftime(config["runtime"]["timestamp_format"])


def _parse_github_url(url: str) -> tuple[str, str]:
    parts = _split_path_parts(url)
    if len(parts) != 2:
        raise ProcessingError(f"Invalid GitHub URL: {url}")
    return parts[0], parts[1]


def _parse_pages_url(url: str) -> tuple[str, str]:
    from urllib.parse import urlparse

    parsed = urlparse(url)
    host_parts = parsed.netloc.split(".")
    if len(host_parts) < 3:
        raise ProcessingError(f"Invalid Pages URL: {url}")

    owner = ".".join(host_parts[:-2])
    parts = _split_path_parts(url)
    if len(parts) != 1:
        raise ProcessingError(f"Invalid Pages URL: {url}")
    return owner, parts[0]


def _split_path_parts(url: str) -> list[str]:
    from urllib.parse import urlparse

    parsed = urlparse(url)
    return [part for part in parsed.path.split("/") if part]
