"""Configuracao de logging por execucao."""

from __future__ import annotations

import logging
from pathlib import Path


def setup_logger(log_path: str | Path, logger_name: str = "hub_pipeline") -> logging.Logger:
    log_file = Path(log_path)
    log_file.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    logger.propagate = False

    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    logger.info("Logger initialised at %s", log_file)
    return logger
