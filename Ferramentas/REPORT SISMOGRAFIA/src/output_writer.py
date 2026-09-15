from __future__ import annotations

import shutil
from pathlib import Path
from typing import Dict

import fitz
from PIL import Image

from .artifacts import build_artifact_context, resolve_artifact_name
from .charts import make_all_charts
from .exceptions import OutputError
from .io_utils import save_json, write_text
from .report import build_pdf_report, render_pdf_to_png
from .whatsapp import build_whatsapp_note


def _ensure_non_empty_file(path: Path, label: str) -> None:
    if not path.exists() or path.stat().st_size == 0:
        raise OutputError(f"Failed to create {label}: {path}")


def _validate_report_artifacts(pdf_path: Path, png_path: Path, records: list[Dict], config: Dict) -> None:
    """Validate that the binary report artifacts are readable and structurally useful."""
    try:
        pdf = fitz.open(str(pdf_path))
        try:
            page_count = len(pdf)
            if page_count < 1 or (len(records) <= 3 and page_count != 1):
                raise OutputError(
                    f"Unexpected report page count: {page_count} for {len(records)} point(s)."
                )
            first_page_text = pdf[0].get_text()
        finally:
            pdf.close()
    except OutputError:
        raise
    except Exception as exc:
        raise OutputError(f"Generated PDF cannot be opened: {pdf_path}") from exc

    report_text = config.get("report_text", {})
    required_labels = (
        report_text.get("pressure_chart_title", "Pressão Sonora x Distância"),
        report_text.get("vibration_chart_title", "PPV x Limite ABNT"),
    )
    missing_labels = [label for label in required_labels if str(label) not in first_page_text]
    if missing_labels:
        raise OutputError(f"Generated PDF is missing required labels: {missing_labels}")

    try:
        with Image.open(png_path) as image:
            width, height = image.size
            if image.format != "PNG" or image.mode not in {"RGB", "RGBA"}:
                raise OutputError(f"Generated PNG has an unsupported format: {png_path}")
            if width < 1000 or height < 1400:
                raise OutputError(f"Generated PNG resolution is too small: {width}x{height}")
            if abs((width / height) - (595.28 / 841.89)) > 0.01:
                raise OutputError(f"Generated PNG is not A4-proportioned: {width}x{height}")
            image.verify()
    except OutputError:
        raise
    except Exception as exc:
        raise OutputError(f"Generated PNG cannot be opened: {png_path}") from exc


def _copy_input_files(input_path: str | Path, out_dir: Path) -> list[Path]:
    raw_dir = out_dir / "entrada_csv"
    raw_dir.mkdir(parents=True, exist_ok=True)
    source = Path(input_path)
    files = [source] if source.is_file() else list(source.rglob("*.csv"))
    copied: list[Path] = []
    for src in files:
        if src.exists():
            destination = raw_dir / src.name
            shutil.copy2(src, destination)
            copied.append(destination)
    return copied


def write_campaign_outputs(records: list[Dict], summary: Dict, config: Dict, input_path: str | Path, out_dir: str | Path, logger=None, log_file: str | Path | None = None) -> Dict:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    copied_inputs = _copy_input_files(input_path, out_dir)

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

    for label, path in {
        "json": json_path,
        "whatsapp_note": note_path,
        "pdf": pdf_path,
        "png": png_path,
        "pressure_chart": Path(charts["pressure_chart"]),
        "vibration_chart": Path(charts["vibration_chart"]),
    }.items():
        _ensure_non_empty_file(Path(path), label)
    for path in copied_inputs:
        _ensure_non_empty_file(path, "copied input CSV")
    if log_file is not None:
        _ensure_non_empty_file(Path(log_file), "execution log")
    _validate_report_artifacts(pdf_path, png_path, records, config)
    save_json(manifest, manifest_path)
    _ensure_non_empty_file(manifest_path, "manifest")

    if logger:
        logger.info("Output artifacts written to %s", out_dir)

    return manifest
