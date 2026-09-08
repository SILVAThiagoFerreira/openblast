"""Sincronizacao do manifesto gerado com o HTML do front-end."""

from __future__ import annotations

import json
import re
from pathlib import Path

from .exceptions import OutputError


MANIFEST_MARKER_START = "<!-- MANIFEST:START -->"
MANIFEST_MARKER_END = "<!-- MANIFEST:END -->"
MANIFEST_SCRIPT_ID = "initial-manifest"
SCRIPT_SRC_PATTERN = re.compile(r'(<script\b[^>]*\bsrc="[^"]*script\.js)(?:\?[^" ]*)?(\")')
STYLE_HREF_PATTERN = re.compile(r'(<link\b[^>]*\bhref="[^"]*styles\.css)(?:\?[^" ]*)?(\")')


def sync_manifest_snapshot(index_path: str | Path, manifest_path: str | Path) -> Path:
    index_file = Path(index_path)
    manifest_file = Path(manifest_path)

    if not index_file.exists():
        raise OutputError(f"Frontend HTML not found: {index_file}")
    if not manifest_file.exists():
        raise OutputError(f"Manifest not found for HTML sync: {manifest_file}")

    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    snapshot = json.dumps(manifest, ensure_ascii=False, separators=(",", ":"))
    script_block = (
        f'{MANIFEST_MARKER_START}\n'
        f'<script type="application/json" id="{MANIFEST_SCRIPT_ID}">{snapshot}</script>\n'
        f"{MANIFEST_MARKER_END}"
    )

    html = index_file.read_text(encoding="utf-8")
    start = html.find(MANIFEST_MARKER_START)
    end = html.find(MANIFEST_MARKER_END)

    if start == -1 or end == -1 or end < start:
        raise OutputError(
            f"Missing manifest markers in HTML file {index_file}. "
            "Expected <!-- MANIFEST:START --> and <!-- MANIFEST:END -->."
        )

    end += len(MANIFEST_MARKER_END)
    updated_html = html[:start] + script_block + html[end:]
    run_id = manifest.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        raise OutputError(f"Manifest is missing a valid run_id for asset cache busting: {manifest_file}")
    updated_html = re.sub(
        SCRIPT_SRC_PATTERN,
        rf'\1?v={run_id}\2',
        updated_html,
    )
    updated_html = STYLE_HREF_PATTERN.sub(rf'\1?v={run_id}\2', updated_html)
    index_file.write_text(updated_html, encoding="utf-8")
    return index_file
