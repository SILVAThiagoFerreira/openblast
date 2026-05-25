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


def build_manifest(config: dict, workbook_result, tool_records: list[ToolRecord], run_id: str, generated_at: str) -> dict:
    return {
        "manifest_version": "1.0",
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
            "total_rows": len(workbook_result.rows),
            "valid_rows": len(tool_records),
            "invalid_rows": 0,
        },
        "validation": {
            "status": "passed",
            "error_count": 0,
            "warning_count": 0,
        },
        "generator": {
            "python": platform.python_version(),
            "openpyxl": openpyxl.__version__,
        },
        "tools": [asdict(record) for record in tool_records],
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
