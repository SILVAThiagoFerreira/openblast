from __future__ import annotations

import argparse
import sys
from pathlib import Path

from src.config_loader import load_config
from src.data_reader import read_input_records
from src.exceptions import ProjectError
from src.io_utils import make_output_dir
from src.logger_setup import setup_logging
from src.output_writer import write_campaign_outputs
from src.processor import process_campaign
from src.validator import validate_config, validate_input_records, validate_processed_results


def run_pipeline(input_path: str, config: dict, out_root: str | None = None, logger=None, log_path: Path | None = None) -> dict:
    if out_root:
        config.setdefault("paths", {})["output_root"] = out_root
    validate_config(config)

    if logger is None or log_path is None:
        logger, log_path = setup_logging(config)
    try:
        logger.info("Starting execution with input=%s", input_path)

        records = read_input_records(input_path, logger=logger)
        validate_input_records(records, config)

        processed = process_campaign(records, config, logger=logger)
        validate_processed_results(processed["records"], processed["summary"], config)

        out_dir = make_output_dir(config, processed["records"])
        manifest = write_campaign_outputs(
            processed["records"],
            processed["summary"],
            config,
            input_path,
            out_dir,
            logger=logger,
            log_file=log_path,
        )
        logger.info("Execution completed successfully")
        return manifest
    except Exception:
        logger.exception("Pipeline execution failed")
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description="Gera relatório onepage sismográfico a partir de CSVs de sismógrafos.")
    parser.add_argument("--input", "-i", default=None, help="Pasta ou arquivo CSV de entrada.")
    parser.add_argument("--config", "-c", default="config.json", help="Arquivo config.json.")
    parser.add_argument("--out", "-o", default=None, help="Pasta raiz de saída. Se omitido, usa a configuração.")
    args = parser.parse_args()

    try:
        config = load_config(args.config)
        input_path = args.input or config.get("paths", {}).get("input_dir", "input")
        manifest = run_pipeline(input_path, config, args.out)
    except ProjectError as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # pragma: no cover - safety net for unexpected failures.
        print(f"Erro inesperado: {exc}", file=sys.stderr)
        return 1

    print("\nProjeto executado com sucesso. Arquivos gerados:")
    for key, value in manifest.items():
        print(f"- {key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
