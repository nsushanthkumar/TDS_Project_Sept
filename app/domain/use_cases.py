from __future__ import annotations

from typing import Dict, Any

from app.domain.models import GenerationRequest, RepoInfo, EvalNotification
from app.services.llm_service import LLMService
from app.services.repo_service import RepoService
from app.services.notifier import Notifier
from app.services.evidence_logger import EvidenceLogger


class GenerateAndPublishApp:
    def __init__(self, llm: LLMService, repo: RepoService, notifier: Notifier, evidence: EvidenceLogger):
        self.llm = llm
        self.repo = repo
        self.notifier = notifier
        self.evidence = evidence

    def execute(self, req: GenerationRequest, req_ip: str | None, req_url: str | None) -> Dict[str, Any]:
        current_step = "initialization"
        data_dict = req.model_dump()
        try:
            existing_code = ""
            if req.round > 1 and (req.task or "").strip():
                current_step = "fetching existing code"
                existing_code = self.repo.get_existing_code(req.task or "") or ""

            current_step = "generating code"
            code_files = self.llm.generate_app_code(
                brief=req.brief,
                checks=req.checks,
                attachments=req.attachments or [],
                existing_code=existing_code,
                round_num=req.round,
            )

            current_step = "creating/updating repository"
            repo_info = self.repo.upsert_repo(req.task or "", code_files, req.round)

            current_step = "updating README"
            try:
                self.repo.update_readme(
                    repo_info["repo"],
                    req.task or "",
                    req.brief,
                    repo_info["repo_url"],
                    repo_info["pages_url"],
                )
            except Exception:
                pass

            current_step = "fetching commit info"
            try:
                commits = repo_info["repo"].get_commits()
                latest_commit_sha = commits[0].sha
            except Exception:
                latest_commit_sha = repo_info.get("commit_sha", "unknown")

            eval_payload = EvalNotification(
                email=req.email,
                task=req.task or "",
                round=req.round,
                nonce=req.nonce,
                repo_url=repo_info["repo_url"],
                commit_sha=latest_commit_sha,
                pages_url=repo_info["pages_url"],
            ).model_dump()

            current_step = "notifying evaluation API"
            notify_ok = False
            try:
                notify_ok = self.notifier.notify(req.evaluation_url, eval_payload)
            except Exception:
                notify_ok = False

            response = {
                "status": "success",
                "repo_url": repo_info["repo_url"],
                "pages_url": repo_info["pages_url"],
                "commit_sha": latest_commit_sha,
            }
            if not notify_ok:
                response["warning"] = "Failed to notify evaluation API after retries"

            try:
                self.evidence.log(data_dict, response, req_ip, req_url)
            except Exception:
                pass

            return response

        except Exception as e:
            error_message = str(e)
            if current_step != "initialization":
                error_message = f"Failed at step '{current_step}': {error_message}"
            error_response = {"status": "error", "message": error_message}
            try:
                self.evidence.log(data_dict, error_response, req_ip, req_url)
            except Exception:
                pass
            return error_response

