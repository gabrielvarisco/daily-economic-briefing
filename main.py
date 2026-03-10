import hashlib
import logging
import os
import time
import uuid
from typing import Set

import requests

from Scripts.history_store import save_daily_snapshot
from Scripts.html_report import generate_html_report
from Scripts.logging_utils import configure_logging
from Scripts.pipeline import build_batches, build_health_report, build_sections

logger = logging.getLogger("main")


def send_telegram(message: str, run_id: str, retries: int = 3) -> bool:
    if os.getenv("DRY_RUN_TELEGRAM", "0") == "1":
        logger.info("dry-run telegram enabled", extra={"run_id": run_id, "status": "dry-run"})
        return True

    token = os.environ.get("TELEGRAM_TOKEN")
    chat_id = os.environ.get("CHAT_ID")

    if not token or not chat_id:
        logger.warning("telegram not configured", extra={"run_id": run_id, "status": "skipped"})
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }

    retries = max(1, int(os.getenv("TELEGRAM_RETRIES", str(retries))))

    for attempt in range(retries):
        try:
            response = requests.post(url, json=payload, timeout=20)
            if response.status_code in (429, 500, 502, 503, 504) and attempt < retries - 1:
                backoff_seconds = (2 ** attempt)
                logger.warning(
                    "telegram transient failure",
                    extra={"run_id": run_id, "status": response.status_code},
                )
                time.sleep(backoff_seconds)
                continue

            response.raise_for_status()
            return True

        except requests.RequestException as exc:
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
                continue
            logger.error(f"telegram send failed: {exc}", extra={"run_id": run_id, "status": "error"})
            return False

    return False


def send_report_in_batches(run_id: str) -> tuple[dict, dict, dict]:
    structured_sections, metrics = build_sections(run_id=run_id)
    health_report = build_health_report(metrics)
    batches = build_batches(structured_sections)

    sent_hashes: Set[str] = set()
    for idx, batch in enumerate(batches, start=1):
        if not batch:
            continue

        checksum = hashlib.sha256(batch.encode("utf-8")).hexdigest()
        if checksum in sent_hashes:
            logger.warning("duplicate batch skipped", extra={"run_id": run_id, "status": "deduplicated"})
            continue

        logger.info(f"sending batch {idx}", extra={"run_id": run_id, "status": "sending"})
        send_telegram(batch, run_id=run_id)
        sent_hashes.add(checksum)

    logger.info(f"section metrics: {metrics}", extra={"run_id": run_id, "status": "completed"})
    logger.info(f"health report: {health_report}", extra={"run_id": run_id, "status": "completed"})
    return structured_sections, metrics, health_report


if __name__ == "__main__":
    configure_logging()
    run_id = uuid.uuid4().hex[:10]

    logger.info("starting daily economic briefing", extra={"run_id": run_id, "status": "started"})

    structured_sections, metrics, health_report = send_report_in_batches(run_id=run_id)

    snapshot_path = save_daily_snapshot(
        structured_sections,
        metadata={
            "run_id": run_id,
            "section_metrics": metrics,
            "health_report": health_report,
        },
    )
    logger.info(f"snapshot saved at {snapshot_path}", extra={"run_id": run_id, "status": "ok"})

    report_path, index_path = generate_html_report(structured_sections)
    logger.info(f"html report saved at {report_path}", extra={"run_id": run_id, "status": "ok"})
    logger.info(f"index saved at {index_path}", extra={"run_id": run_id, "status": "ok"})
