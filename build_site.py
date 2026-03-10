import logging
import uuid

from Scripts.history_store import save_daily_snapshot
from Scripts.html_report import generate_html_report
from Scripts.logging_utils import configure_logging
from Scripts.pipeline import build_health_report, build_sections

logger = logging.getLogger("build_site")


if __name__ == "__main__":
    configure_logging()
    run_id = uuid.uuid4().hex[:10]

    logger.info("starting silent site build", extra={"run_id": run_id, "status": "started"})

    structured_sections, metrics = build_sections(run_id=run_id)
    health_report = build_health_report(metrics)

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
    logger.info(f"section metrics: {metrics}", extra={"run_id": run_id, "status": "completed"})
    logger.info(f"health report: {health_report}", extra={"run_id": run_id, "status": "completed"})
