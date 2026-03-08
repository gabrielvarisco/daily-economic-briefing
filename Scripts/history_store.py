import json
import os
from datetime import datetime
from typing import Any, Dict, Optional


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(BASE_DIR, "data")
HISTORY_DIR = os.path.join(DATA_DIR, "history")


def _ensure_dirs() -> None:
    os.makedirs(HISTORY_DIR, exist_ok=True)


def _today_filename(prefix: str = "snapshot") -> str:
    today = datetime.utcnow().strftime("%Y-%m-%d")
    return os.path.join(HISTORY_DIR, f"{prefix}_{today}.json")


def save_daily_snapshot(payload: Dict[str, Any], prefix: str = "snapshot") -> str:
    """
    Salva um snapshot diário em JSON.
    Se já existir arquivo no dia, sobrescreve.
    """
    _ensure_dirs()

    filepath = _today_filename(prefix=prefix)

    content = {
        "generated_at_utc": datetime.utcnow().isoformat(),
        "data": payload,
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(content, f, ensure_ascii=False, indent=2)

    return filepath


def load_latest_snapshot(prefix: str = "snapshot") -> Optional[Dict[str, Any]]:
    """
    Carrega o snapshot mais recente encontrado.
    """
    _ensure_dirs()

    files = [
        f for f in os.listdir(HISTORY_DIR)
        if f.startswith(f"{prefix}_") and f.endswith(".json")
    ]

    if not files:
        return None

    files.sort(reverse=True)
    latest = os.path.join(HISTORY_DIR, files[0])

    with open(latest, "r", encoding="utf-8") as f:
        return json.load(f)


def load_previous_snapshot(prefix: str = "snapshot") -> Optional[Dict[str, Any]]:
    """
    Carrega o snapshot anterior ao mais recente.
    """
    _ensure_dirs()

    files = [
        f for f in os.listdir(HISTORY_DIR)
        if f.startswith(f"{prefix}_") and f.endswith(".json")
    ]

    if len(files) < 2:
        return None

    files.sort(reverse=True)
    previous = os.path.join(HISTORY_DIR, files[1])

    with open(previous, "r", encoding="utf-8") as f:
        return json.load(f)
