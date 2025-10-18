from __future__ import annotations

from typing import Any, List, Optional
from pydantic import BaseModel, Field, validator


class GenerateRequest(BaseModel):
    email: str
    secret: str
    round: int = Field(ge=1)
    nonce: str
    brief: str
    evaluation_url: str
    task: Optional[str] = None
    checks: List[str] = []
    attachments: Optional[list[Any]] = None

    @validator("checks", pre=True, always=True)
    def default_checks(cls, v):
        return v or []


class GenerateResponse(BaseModel):
    status: str
    repo_url: str
    pages_url: str
    commit_sha: str
    warning: Optional[str] = None

