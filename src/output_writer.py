"""Escrita dos artefatos gerados pelo pipeline."""

from __future__ import annotations

import json
from pathlib import Path

from .exceptions import OutputError


def write_json_file(payload: dict, output_path: str | Path, indent: int, ensure_ascii: bool) -> Path:
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temp_path = destination.with_suffix(destination.suffix + ".tmp")

    try:
        temp_path.write_text(
            json.dumps(payload, indent=indent, ensure_ascii=ensure_ascii),
            encoding="utf-8",
        )
        temp_path.replace(destination)
    except OSError as exc:
        raise OutputError(f"Failed to write output file {destination}: {exc}") from exc

    return destination


def write_manifest(manifest: dict, output_path: str | Path, output_config: dict) -> Path:
    return write_json_file(manifest, output_path, output_config["indent"], output_config["ensure_ascii"])


def write_summary(summary: dict, output_path: str | Path, output_config: dict) -> Path:
    return write_json_file(summary, output_path, output_config["indent"], output_config["ensure_ascii"])
