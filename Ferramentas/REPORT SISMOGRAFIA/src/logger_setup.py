from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Tuple


def setup_logging(config: Dict, run_context: Dict[str, str] | None = None) -> tuple[logging.Logger, Path]:
    run_context = run_context or {
        "date": datetime.now().strftime("%Y%m%d"),
        "time": datetime.now().strftime("%H%M%S"),
        "file_prefix": config.get("output", {}).get("file_prefix", "ENAEX_NSR"),
        "folder_prefix": config.get("output", {}).get("folder_prefix", "monitoramento_sismografico"),
    }
    logging_cfg = config.get("logging", {})
    paths_cfg = config.get("paths", {})
    logs_root = Path(paths_cfg.get("logs_root", "logs"))
    logs_root.mkdir(parents=True, exist_ok=True)

    file_template = logging_cfg.get("file_template", "{file_prefix}-{date}_{time}.log")
    log_path = logs_root / file_template.format(**run_context)

    logger = logging.getLogger("sismo_report")
    logger.handlers.clear()
    logger.setLevel(getattr(logging, str(logging_cfg.get("level", "INFO")).upper(), logging.INFO))
    logger.propagate = False

    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    logger.info("Logging initialized at %s", log_path)
    return logger, log_path
