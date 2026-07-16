from __future__ import annotations

import shutil
from pathlib import Path
from typing import Dict

from .artifacts import build_artifact_context, resolve_artifact_name
from .charts import make_all_charts
from .exceptions import OutputError
from .io_utils import save_json, write_text
from .report import build_pdf_report, render_pdf_to_png
from .whatsapp import build_whatsapp_note


def _ensure_non_empty_file(path: Path, label: str) -> None:
    if not path.exists() or path.stat().st_size == 0:
        raise OutputError(f"Failed to create {label}: {path}")


def _copy_input_files(input_path: str | Path, out_dir: Path) -> None:
    raw_dir = out_dir / "entrada_csv"
    raw_dir.mkdir(parents=True, exist_ok=True)
    source = Path(input_path)
    files = [source] if source.is_file() else list(source.rglob("*.csv"))
    for src in files:
        if src.exists():
            shutil.copy2(src, raw_dir / src.name)


def write_campaign_outputs(records: list[Dict], summary: Dict, config: Dict, input_path: str | Path, out_dir: str | Path, logger=None, log_file: str | Path | None = None) -> Dict:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    _copy_input_files(input_path, out_dir)

    context = build_artifact_context(config, event_date=summary.get("event_date"))
    charts = make_all_charts(records, config, out_dir / "graficos", context)

    payload = {
        "summary": summary,
        "config_limits": config.get("limits", {}),
        "records": records,
    }

    json_path = out_dir / resolve_artifact_name(config, "data_json", context)
    note_path = out_dir / resolve_artifact_name(config, "whatsapp_note", context)
    pdf_path = out_dir / resolve_artifact_name(config, "report_pdf", context)
    png_path = out_dir / resolve_artifact_name(config, "report_png", context)
    manifest_path = out_dir / resolve_artifact_name(config, "manifest_json", context)

    save_json(payload, json_path)
    note = build_whatsapp_note(records, summary, config)
    write_text(note, note_path)
    build_pdf_report(records, summary, config, charts, pdf_path)
    render_pdf_to_png(pdf_path, png_path)

    manifest = {
        "output_dir": str(out_dir),
        "pdf": str(pdf_path),
        "png": str(png_path),
        "whatsapp_note": str(note_path),
        "json": str(json_path),
        "charts": charts,
        "manifest": str(manifest_path),
    }
    if log_file is not None:
        manifest["log_file"] = str(log_file)
    save_json(manifest, manifest_path)

    for label, path in {
        "json": json_path,
        "whatsapp_note": note_path,
        "pdf": pdf_path,
        "png": png_path,
        "manifest": manifest_path,
        "pressure_chart": Path(charts["pressure_chart"]),
        "vibration_chart": Path(charts["vibration_chart"]),
    }.items():
        _ensure_non_empty_file(Path(path), label)

    if logger:
        logger.info("Output artifacts written to %s", out_dir)

    return manifest
