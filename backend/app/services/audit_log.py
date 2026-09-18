"""Minimal structured audit log for safety events."""
import json
import time
from pathlib import Path

_LOG_PATH = Path("logs/safety_audit.log")
_LOG_PATH.parent.mkdir(exist_ok=True)


def audit(event: str, **fields) -> None:
    rec = {"ts": time.time(), "event": event, **fields}
    try:
        with _LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, default=str) + "\n")
    except Exception:
        pass
