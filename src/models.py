"""Modelos de dados utilizados pelo pipeline."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class WorkbookRow:
    row_number: int
    repository_id: str
    formal_title: str
    github_url: str
    pages_url: str


@dataclass(frozen=True)
class WorkbookReadResult:
    source_path: Path
    sheet_name: str
    headers: list[str]
    rows: list[WorkbookRow]
    source_hash: str


@dataclass(frozen=True)
class ToolRecord:
    row_number: int
    repository_id: str
    formal_title: str
    github_url: str
    pages_url: str
    description: str
    kind: str
    accent: str
    accent2: str
    github_owner: str
    github_repo_name: str
    pages_owner: str
    pages_repo_name: str
    order: int


@dataclass(frozen=True)
class ValidationIssue:
    severity: str
    code: str
    message: str
    row_number: int | None = None
    field_name: str | None = None


@dataclass
class ValidationReport:
    issues: list[ValidationIssue] = field(default_factory=list)
    row_count: int = 0

    def add_issue(self, issue: ValidationIssue) -> None:
        self.issues.append(issue)

    @property
    def error_count(self) -> int:
        return sum(1 for issue in self.issues if issue.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for issue in self.issues if issue.severity == "warning")

    @property
    def is_valid(self) -> bool:
        return self.error_count == 0

    def to_dict(self) -> dict:
        return {
            "row_count": self.row_count,
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "is_valid": self.is_valid,
            "issues": [asdict(issue) for issue in self.issues],
        }
