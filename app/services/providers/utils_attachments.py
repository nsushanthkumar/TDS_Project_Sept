from __future__ import annotations

from typing import Any, Dict, Optional


MAX_FULL_CONTENT_CHARS = 20000
MAX_PREVIEW_LINES = 10


def process_all_attachments(attachments: Optional[list]) -> str:
    if not attachments:
        return ""

    # Minimal, stable summary to keep behavior similar to original
    result = "\n\n=== ATTACHMENTS ===\n"
    for i, att in enumerate(attachments, 1):
        # Only include safe, small hints to not balloon the prompt
        if isinstance(att, dict):
            name = att.get("name") or att.get("filename") or "attachment"
            url = att.get("url") or att.get("type") or att.get("mime") or ""
            result += f"--- {name} ---\n"
            if url:
                result += f"Ref: {str(url)[:120]}\n\n"
            else:
                result += "Ref: inline\n\n"
        elif isinstance(att, str):
            preview = att[:100]
            result += f"--- attachment ---\nRef: {preview}\n\n"
        else:
            result += f"--- attachment ---\nRef: {type(att).__name__}\n\n"

    return result

