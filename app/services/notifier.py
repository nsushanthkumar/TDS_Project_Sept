from __future__ import annotations

from typing import Dict, Any

import time
from typing import Dict, Any
import requests


class Notifier:
    def notify(self, evaluation_url: str, data: Dict[str, Any], max_retries: int = 5) -> bool:
        delay = 1
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    evaluation_url,
                    json=data,
                    headers={"Content-Type": "application/json"},
                    timeout=30,
                )
                if response.status_code == 200:
                    return True
            except requests.RequestException:
                pass
            if attempt < max_retries - 1:
                time.sleep(delay)
                delay *= 2
        return False
