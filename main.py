"""Ponto de entrada unico do pipeline do hub."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

from src.config_loader import build_runtime_paths, ensure_runtime_directories, load_config
from src.data_reader import read_workbook
from src.exceptions import ConfigError, PipelineError
from src.frontend_sync import sync_manifest_snapshot
from src.logger_setup import setup_logger
from src.output_writer import write_manifest, write_summary
from src.processor import build_manifest, build_summary, build_tool_records, make_timestamp
from src.validator import validate_inputs


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the OpenBlast US MVV tool manifest pipeline")
    parser.add_argument("--config", default="config.json", help="Path to the JSON config file")
    return parser.parse_args(argv)


def run_pipeline(config_path: str | Path) -> int:
    config = load_config(config_path)
    run_id = datetime.now(timezone.utc).strftime(config["runtime"]["run_id_format"])
    generated_at = make_timestamp(config)
    runtime_paths = build_runtime_paths(config, run_id)
    ensure_runtime_directories(runtime_paths)

    logger = setup_logger(runtime_paths["log_file"])
    logger.info("Pipeline started | run_id=%s", run_id)

    workbook_result = None
    validation_report = None
    summary_path = runtime_paths["summary_file"]
    published_targets: list[dict] = []

    try:
        workbook_result = read_workbook(
            runtime_paths["input_workbook"],
            config["workbook"]["sheet_name"],
            config["workbook"]["header_row"],
            logger,
        )
        validation_report = validate_inputs(config, workbook_result)
        logger.info(
            "Validation completed | errors=%d | warnings=%d",
            validation_report.error_count,
            validation_report.warning_count,
        )

        if not validation_report.is_valid:
            summary = build_summary(
                config,
                workbook_result,
                validation_report,
                run_id,
                generated_at,
                status="failed",
                stage="validation",
                message="Validation failed",
                manifest_path=None,
                summary_path=str(summary_path),
                log_path=str(runtime_paths["log_file"]),
                published_targets=published_targets,
            )
            write_summary(summary, summary_path, config["output"])
            logger.error("Validation failed | run_id=%s", run_id)
            return 1

        tool_records = build_tool_records(config, workbook_result)
        for target in runtime_paths["publication_targets"]:
            manifest = build_manifest(
                config,
                workbook_result,
                tool_records,
                run_id,
                generated_at,
                publication_target=target,
            )
            write_manifest(manifest, target["manifest_file"], config["output"])
            sync_manifest_snapshot(target["html_file"], target["manifest_file"])
            published_targets.append(
                {
                    "slug": target["slug"],
                    "manifest": str(target["manifest_file"]),
                    "html": str(target["html_file"]),
                    "hub_slugs": target["hub_slugs"],
                    "hub_count": manifest["counts"]["hub_count"],
                    "tool_count": manifest["counts"]["valid_rows"],
                }
            )

        summary = build_summary(
            config,
            workbook_result,
            validation_report,
            run_id,
            generated_at,
            status="success",
            stage="complete",
            message="Pipeline completed successfully",
            manifest_path=str(runtime_paths["manifest_file"]),
            summary_path=str(summary_path),
            log_path=str(runtime_paths["log_file"]),
            published_targets=published_targets,
        )
        write_summary(summary, summary_path, config["output"])

        logger.info("Internal manifest written to %s", runtime_paths["manifest_file"])
        logger.info("Internal HTML synchronized at %s", runtime_paths["index_file"])
        for target in published_targets:
            logger.info(
                "Published target %s | manifest=%s | html=%s | hubs=%s | tools=%d",
                target["slug"],
                target["manifest"],
                target["html"],
                ",".join(target["hub_slugs"]),
                target["tool_count"],
            )
        logger.info("Summary written to %s", summary_path)
        logger.info("Pipeline completed successfully | run_id=%s", run_id)
        return 0
    except PipelineError as exc:
        logger.exception("Pipeline failed | run_id=%s | error=%s", run_id, exc)
        summary = build_summary(
            config,
            workbook_result,
            validation_report,
            run_id,
            generated_at,
            status="failed",
            stage="runtime",
            message=str(exc),
            manifest_path=None,
            summary_path=str(summary_path),
            log_path=str(runtime_paths["log_file"]),
            published_targets=published_targets,
        )
        try:
            write_summary(summary, summary_path, config["output"])
        except Exception:  # pragma: no cover - best effort logging
            logger.exception("Could not write failure summary")
        return 1


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        return run_pipeline(args.config)
    except ConfigError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # pragma: no cover - defensive guard
        print(f"Unexpected error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
