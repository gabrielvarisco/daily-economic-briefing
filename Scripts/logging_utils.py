import json
import logging
import os
import sys
from datetime import datetime
from typing import Any, Dict, Optional


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: Dict[str, Any] = {
            "ts": datetime.utcnow().isoformat(timespec="seconds") + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        for key in ("run_id", "section", "status", "elapsed_ms"):
            value = getattr(record, key, None)
            if value is not None:
                payload[key] = value

        return json.dumps(payload, ensure_ascii=False)


def configure_logging(level: Optional[str] = None) -> None:
    logger = logging.getLogger()
    if logger.handlers:
        return

    raw_level = (level or os.getenv("LOG_LEVEL") or "INFO").upper()
    log_level = getattr(logging, raw_level, logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())

    logger.setLevel(log_level)
    logger.addHandler(handler)

    third_party_level = os.getenv("THIRD_PARTY_LOG_LEVEL", "ERROR").upper()
    lib_level = getattr(logging, third_party_level, logging.ERROR)
    logging.getLogger("yfinance").setLevel(lib_level)
    logging.getLogger("urllib3").setLevel(lib_level)
