from __future__ import annotations

from typing import Dict, Optional

from app.services.vcs.github_manager import (
    create_or_update_repo as gh_create_or_update_repo,
    update_readme as gh_update_readme,
    get_existing_code as gh_get_existing_code,
)


class RepoService:
    def get_existing_code(self, task: str, path: str = "index.html") -> Optional[str]:
        return gh_get_existing_code(task, path)

    def upsert_repo(self, task: str, code_files: Dict[str, str], round_num: int):
        return gh_create_or_update_repo(task, code_files, round_num)

    def update_readme(self, repo, task: str, brief: str, repo_url: str, pages_url: str):
        return gh_update_readme(repo, task, brief, repo_url, pages_url)
