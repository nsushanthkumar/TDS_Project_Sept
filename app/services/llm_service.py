from __future__ import annotations

from typing import Dict, Optional

from app.services.providers.llm_openai import (
    generate_app_code as provider_generate_app_code,
    generate_readme as provider_generate_readme,
)


class LLMService:
    def generate_app_code(
        self,
        brief: str,
        checks: list | None,
        attachments: Optional[list],
        existing_code: Optional[str],
        round_num: int,
    ) -> Dict[str, str]:
        return provider_generate_app_code(
            brief, checks or [], attachments, existing_code, round_num
        )

    def generate_readme(self, task: str, brief: str, repo_url: str, pages_url: str) -> str:
        return provider_generate_readme(task, brief, repo_url, pages_url)
