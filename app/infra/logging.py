import json
import logging
import sys
from typing import Any, Dict


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:  # type: ignore[override]
        payload: Dict[str, Any] = {
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
        }
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        # Attach extra fields if present
        for key, value in getattr(record, "__dict__", {}).items():
            if key.startswith("_"):
                continue
            if key in payload:
                continue
            # only include simple JSON-serializable extras
            if isinstance(value, (str, int, float, bool, type(None), dict, list)):
                payload[key] = value
        return json.dumps(payload, ensure_ascii=False)


def setup_logging(level: int = logging.INFO) -> None:
    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(JsonFormatter())

    root = logging.getLogger()
    root.setLevel(level)
    # Clear existing handlers to avoid duplicates on repeated factory calls
    root.handlers.clear()
    root.addHandler(handler)

