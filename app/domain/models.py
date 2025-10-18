from __future__ import annotations

from typing import Any, List, Optional
from pydantic import BaseModel, Field


class GenerationRequest(BaseModel):
    email: str
    secret: str
    round: int = Field(ge=1)
    nonce: str
    brief: str
    evaluation_url: str
    task: Optional[str] = None
    checks: List[str] = []
    attachments: Optional[list[Any]] = None


class RepoInfo(BaseModel):
    repo_url: str
    pages_url: str
    commit_sha: str
    # Keep raw repo object optional for internal use
    _repo: Any | None = None  # type: ignore


class EvalNotification(BaseModel):
    email: str
    task: str
    round: int
    nonce: str
    repo_url: str
    commit_sha: str
    pages_url: str

