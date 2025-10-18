from __future__ import annotations

from typing import Dict, Optional
import requests
import time
from github import Github, GithubException

from app.infra.settings import get_settings
from app.services.vcs.html_assets import process_html_assets


def _client() -> Github:
    return Github(get_settings().github_token)


def get_existing_code(task: str, path: str = "index.html") -> Optional[str]:
    try:
        user = _client().get_user()
        try:
            repo = user.get_repo(task)
        except GithubException as e:
            if e.status in (403, 404):
                return None
            return None

        try:
            contents = repo.get_contents(path, ref="main")
            if hasattr(contents, "decoded_content"):
                return contents.decoded_content.decode("utf-8")
            return None
        except GithubException as e:
            if e.status == 404:
                return None
            return None
    except Exception:
        return None


def _mit_license() -> str:
    year = "2025"
    name = get_settings().github_username or "Student"
    return f"""MIT License

Copyright (c) {year} {name}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


def create_or_update_repo(task: str, code_files: Dict[str, str], round_num: int) -> Dict[str, str]:
    user = _client().get_user()
    repo_name = task
    owner = user.login

    try:
        repo = user.get_repo(repo_name)
    except GithubException as e:
        if e.status == 404:
            repo = user.create_repo(
                name=repo_name,
                description=f"Generated app for task: {task}",
                private=False,
                auto_init=False,
            )
            # Add LICENSE on creation (best effort)
            try:
                repo.create_file(path="LICENSE", message="Add MIT License", content=_mit_license())
            except Exception:
                pass
        else:
            raise

    # Process index.html assets
    index_content = code_files.get("index.html", "")
    index_content = process_html_assets(index_content, repo, round_num)

    # Upsert index.html
    try:
        existing = repo.get_contents("index.html", ref="main")
        repo.update_file(path="index.html", message=f"Update index.html (round {round_num})", content=index_content, sha=existing.sha, branch="main")
    except GithubException as e:
        if e.status == 404:
            repo.create_file(path="index.html", message=f"Add index.html (round {round_num})", content=index_content, branch="main")
        else:
            raise

    # Ensure Pages
    base = "https://api.github.com"
    token = get_settings().github_token
    hdrs = {"Authorization": f"token {token}", "Accept": "application/vnd.github+json"}
    branch = "main"

    try:
        r = requests.get(f"{base}/repos/{owner}/{repo_name}/pages", headers=hdrs, timeout=10)
        if r.status_code == 404:
            cr = requests.post(f"{base}/repos/{owner}/{repo_name}/pages", headers=hdrs, json={"source": {"branch": branch, "path": "/"}}, timeout=10)
            if cr.status_code not in (201, 202):
                pass
    except Exception:
        pass

    pages_url = f"https://{owner}.github.io/{repo_name}/"
    try:
        commits = repo.get_commits()
        latest_commit_sha = commits[0].sha
    except Exception:
        latest_commit_sha = "unknown"

    return {
        "repo": repo,
        "repo_url": repo.html_url,
        "commit_sha": latest_commit_sha,
        "pages_url": pages_url,
    }


def update_readme(repo, task: str, brief: str, repo_url: str, pages_url: str):
    from app.services.llm_service import LLMService

    content = LLMService().generate_readme(task, brief, repo_url, pages_url)
    if not content:
        return
    try:
        readme_file = repo.get_contents("README.md")
        repo.update_file(path="README.md", message="Update README", content=content, sha=readme_file.sha)
    except GithubException as e:
        if e.status == 404:
            repo.create_file(path="README.md", message="Add README", content=content)
        else:
            pass

