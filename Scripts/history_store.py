import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(BASE_DIR, "data")
HISTORY_DIR = os.path.join(DATA_DIR, "history")


def _ensure_dirs() -> None:
    os.makedirs(HISTORY_DIR, exist_ok=True)


def _snapshot_path_for_date(date_str: str, prefix: str = "snapshot") -> str:
    return os.path.join(HISTORY_DIR, f"{prefix}_{date_str}.json")


def _list_snapshot_files(prefix: str = "snapshot") -> List[str]:
    _ensure_dirs()

    files = [
        f for f in os.listdir(HISTORY_DIR)
        if f.startswith(f"{prefix}_") and f.endswith(".json")
    ]

    files.sort(reverse=True)
    return files


def _extract_date_from_filename(filename: str, prefix: str = "snapshot") -> Optional[str]:
    expected_prefix = f"{prefix}_"
    if not filename.startswith(expected_prefix) or not filename.endswith(".json"):
        return None

    return filename[len(expected_prefix):-5]


def save_daily_snapshot(payload: Dict[str, Any], prefix: str = "snapshot") -> str:
    """
    Salva ou sobrescreve o snapshot do dia atual.
    """
    _ensure_dirs()

    today = datetime.utcnow().strftime("%Y-%m-%d")
    filepath = _snapshot_path_for_date(today, prefix=prefix)

    content = {
        "generated_at_utc": datetime.utcnow().isoformat(),
        "snapshot_date_utc": today,
        "data": payload,
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(content, f, ensure_ascii=False, indent=2)

    return filepath


def load_latest_snapshot(prefix: str = "snapshot") -> Optional[Dict[str, Any]]:
    files = _list_snapshot_files(prefix=prefix)

    if not files:
        return None

    latest = os.path.join(HISTORY_DIR, files[0])

    with open(latest, "r", encoding="utf-8") as f:
        return json.load(f)


def load_previous_snapshot(prefix: str = "snapshot") -> Optional[Dict[str, Any]]:
    files = _list_snapshot_files(prefix=prefix)

    if len(files) < 2:
        return None

    previous = os.path.join(HISTORY_DIR, files[1])

    with open(previous, "r", encoding="utf-8") as f:
        return json.load(f)


def load_previous_day_snapshot(prefix: str = "snapshot") -> Optional[Dict[str, Any]]:
    """
    Carrega o snapshot mais recente anterior ao snapshot de hoje.
    Útil para comparação vs ontem/último dia salvo.
    """
    files = _list_snapshot_files(prefix=prefix)

    if not files:
        return None

    today = datetime.utcnow().strftime("%Y-%m-%d")

    candidates = []
    for filename in files:
        date_str = _extract_date_from_filename(filename, prefix=prefix)
        if not date_str:
            continue
        if date_str < today:
            candidates.append(filename)

    if not candidates:
        return None

    candidates.sort(reverse=True)
    filepath = os.path.join(HISTORY_DIR, candidates[0])

    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)
