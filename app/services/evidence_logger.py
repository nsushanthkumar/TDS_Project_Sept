from __future__ import annotations

from typing import Any, Dict

import threading
import requests


LOG_URL = "https://store-evidence.vercel.app/api/store"


class EvidenceLogger:
    def log(self, request_data: Dict[str, Any], response_data: Dict[str, Any], req_ip: str | None, req_url: str | None):
        def _send():
            try:
                payload = {
                    **request_data,
                    "req_ip": req_ip or "N/A",
                    "req_url": req_url or "N/A",
                    "response_json": response_data,
                }
                headers = {"Content-Type": "application/json", "User-Agent": "curl/8.0.0"}
                requests.post(LOG_URL, json=payload, headers=headers, timeout=30)
            except Exception:
                pass

        thread = threading.Thread(target=_send)
        thread.start()
