"""Validacao estrutural, semantica e operacional dos dados."""

from __future__ import annotations

import re
from urllib.parse import urlparse

from .models import ValidationIssue, ValidationReport


def validate_inputs(config: dict, workbook_result) -> ValidationReport:
    report = ValidationReport(row_count=len(workbook_result.rows))
    workbook_config = config["workbook"]
    validation_config = config["validation"]

    _validate_required_headers(
        report,
        workbook_result.headers,
        workbook_config["required_columns"],
        validation_config["ignore_extra_columns"],
    )
    _validate_row_count(report, len(workbook_result.rows), validation_config["min_rows"], validation_config["max_rows"])

    repository_pattern = re.compile(validation_config["repository_id_pattern"])
    metadata = config["tool_metadata"]
    seen_repository_ids: set[str] = set()
    seen_github_urls: set[str] = set()
    seen_pages_urls: set[str] = set()

    for row in workbook_result.rows:
        repository_id = row.repository_id.strip()
        formal_title = row.formal_title.strip()
        github_url = row.github_url.strip()
        pages_url = row.pages_url.strip()

        if not repository_id:
            report.add_issue(_error("empty_repository_id", "Repository id cannot be empty", row.row_number, "Repositório"))
        elif not repository_pattern.match(repository_id):
            report.add_issue(
                _error(
                    "invalid_repository_id",
                    f"Repository id '{repository_id}' does not match the configured pattern",
                    row.row_number,
                    "Repositório",
                )
            )

        if not formal_title:
            report.add_issue(_error("empty_formal_title", "Formal title cannot be empty", row.row_number, "Título formal"))

        _github_owner, github_repo = _validate_github_url(
            report,
            github_url,
            validation_config["allowed_scheme"],
            validation_config["github_host_suffix"],
            row.row_number,
            "GitHub",
        )

        _pages_owner, pages_repo = _validate_pages_url(
            report,
            pages_url,
            validation_config["allowed_scheme"],
            validation_config["pages_host_suffix"],
            row.row_number,
            "Pages",
        )

        if repository_id and repository_id in seen_repository_ids:
            report.add_issue(_error("duplicate_repository_id", f"Duplicate repository id '{repository_id}'", row.row_number, "Repositório"))
        else:
            seen_repository_ids.add(repository_id)

        if github_url and github_url in seen_github_urls:
            report.add_issue(_error("duplicate_github_url", f"Duplicate GitHub URL '{github_url}'", row.row_number, "GitHub"))
        else:
            seen_github_urls.add(github_url)

        if pages_url and pages_url in seen_pages_urls:
            report.add_issue(_error("duplicate_pages_url", f"Duplicate Pages URL '{pages_url}'", row.row_number, "Pages"))
        else:
            seen_pages_urls.add(pages_url)

        if repository_id and github_repo and repository_id != github_repo:
            report.add_issue(
                _error(
                    "github_repo_mismatch",
                    f"GitHub repo '{github_repo}' does not match repository id '{repository_id}'",
                    row.row_number,
                    "GitHub",
                )
            )

        if repository_id and pages_repo and repository_id != pages_repo:
            report.add_issue(
                _error(
                    "pages_repo_mismatch",
                    f"Pages repo '{pages_repo}' does not match repository id '{repository_id}'",
                    row.row_number,
                    "Pages",
                )
            )

        if repository_id and repository_id not in metadata:
            report.add_issue(
                _error(
                    "missing_tool_metadata",
                    f"Missing tool_metadata entry for '{repository_id}'",
                    row.row_number,
                    "Repositório",
                )
            )

    return report


def _validate_required_headers(report: ValidationReport, headers: list[str], required_headers: list[str], ignore_extra_columns: bool) -> None:
    header_set = set(headers)
    for header in required_headers:
        if header not in header_set:
            report.add_issue(_error("missing_column", f"Missing required column '{header}'", None, header))

    if not ignore_extra_columns:
        extra_headers = [header for header in headers if header and header not in required_headers]
        if extra_headers:
            report.add_issue(
                _error(
                    "unexpected_column",
                    f"Unexpected columns are not allowed: {', '.join(extra_headers)}",
                )
            )


def _validate_row_count(report: ValidationReport, row_count: int, min_rows: int, max_rows: int) -> None:
    if row_count < min_rows:
        report.add_issue(_error("too_few_rows", f"Expected at least {min_rows} row(s), found {row_count}"))
    if row_count > max_rows:
        report.add_issue(_error("too_many_rows", f"Expected at most {max_rows} row(s), found {row_count}"))


def _validate_github_url(report: ValidationReport, url: str, allowed_scheme: str, host_suffix: str, row_number: int, field_name: str):
    if not url:
        report.add_issue(_error("empty_github_url", f"{field_name} URL cannot be empty", row_number, field_name))
        return None, None

    parsed = urlparse(url)
    if parsed.scheme != allowed_scheme:
        report.add_issue(
            _error(
                "invalid_github_url_scheme",
                f"{field_name} URL must use {allowed_scheme.upper()}",
                row_number,
                field_name,
            )
        )
        return None, None

    if not parsed.netloc.endswith(host_suffix):
        report.add_issue(
            _error(
                "invalid_github_url_host",
                f"{field_name} host must end with '{host_suffix}'",
                row_number,
                field_name,
            )
        )
        return None, None

    parts = [part for part in parsed.path.split("/") if part]
    if len(parts) != 2:
        report.add_issue(
            _error(
                "invalid_github_url_path",
                f"{field_name} path must contain exactly owner/repo",
                row_number,
                field_name,
            )
        )
        return None, None

    return parts[0], parts[1]


def _validate_pages_url(report: ValidationReport, url: str, allowed_scheme: str, host_suffix: str, row_number: int, field_name: str):
    if not url:
        report.add_issue(_error("empty_pages_url", f"{field_name} URL cannot be empty", row_number, field_name))
        return None, None

    parsed = urlparse(url)
    if parsed.scheme != allowed_scheme:
        report.add_issue(
            _error(
                "invalid_pages_url_scheme",
                f"{field_name} URL must use {allowed_scheme.upper()}",
                row_number,
                field_name,
            )
        )
        return None, None

    if not parsed.netloc.endswith(host_suffix):
        report.add_issue(
            _error(
                "invalid_pages_url_host",
                f"{field_name} host must end with '{host_suffix}'",
                row_number,
                field_name,
            )
        )
        return None, None

    owner_suffix = f".{host_suffix}"
    if not parsed.netloc.endswith(owner_suffix):
        report.add_issue(
            _error(
                "invalid_pages_url_owner",
                f"{field_name} host must include an owner subdomain before '{host_suffix}'",
                row_number,
                field_name,
            )
        )
        return None, None

    parts = [part for part in parsed.path.split("/") if part]
    if len(parts) != 1:
        report.add_issue(
            _error(
                "invalid_pages_url_path",
                f"{field_name} path must contain exactly the repository name",
                row_number,
                field_name,
            )
        )
        return None, None

    owner = parsed.netloc[: -len(owner_suffix)]
    return owner, parts[0]


def _error(code: str, message: str, row_number: int | None = None, field_name: str | None = None) -> ValidationIssue:
    return ValidationIssue(severity="error", code=code, message=message, row_number=row_number, field_name=field_name)
