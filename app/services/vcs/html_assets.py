from __future__ import annotations

import base64
import re
from typing import List, Tuple
from github import GithubException


def _extract_data_uris(html: str, size_threshold: int = 10000) -> List[Tuple[str, str, str]]:
    pattern = r'data:([^;,]+);base64,([A-Za-z0-9+/=]+)'
    matches = []
    for match in re.finditer(pattern, html):
        full_uri = match.group(0)
        mime_type = match.group(1)
        base64_data = match.group(2)
        estimated_size = len(base64_data) * 3 // 4
        if estimated_size >= size_threshold:
            matches.append((full_uri, mime_type, base64_data))
    return matches


def _mime_to_ext(mime_type: str) -> str:
    mapping = {
        'image/png': 'png', 'image/jpeg': 'jpg', 'image/jpg': 'jpg', 'image/gif': 'gif', 'image/svg+xml': 'svg',
        'image/webp': 'webp', 'image/bmp': 'bmp', 'image/x-icon': 'ico', 'image/ico': 'ico', 'image/icon': 'ico',
        'video/mp4': 'mp4', 'video/webm': 'webm', 'video/ogg': 'ogv', 'video/avi': 'avi', 'video/mpeg': 'mpg',
        'audio/mpeg': 'mp3', 'audio/ogg': 'ogg', 'audio/wav': 'wav', 'audio/webm': 'weba', 'audio/aac': 'aac',
        'application/pdf': 'pdf', 'text/plain': 'txt', 'text/css': 'css', 'text/javascript': 'js', 'application/javascript': 'js',
    }
    mime_type = mime_type.lower().strip()
    if mime_type in mapping:
        return mapping[mime_type]
    if '/' in mime_type:
        subtype = mime_type.split('/')[-1].split(';')[0].strip()
        return subtype
    return 'bin'


def _upload_asset(repo, filename: str, content: bytes, message: str, subdir: str = "assets") -> str:
    path = f"{subdir}/{filename}" if subdir else filename
    try:
        try:
            existing = repo.get_contents(path, ref="main")
            repo.update_file(path=path, message=message, content=content, sha=existing.sha, branch="main")
        except GithubException as e:
            if e.status == 404:
                repo.create_file(path=path, message=message, content=content, branch="main")
            else:
                raise
    except Exception:
        raise
    return path


def process_html_assets(html: str, repo, round_num: int = 1) -> str:
    data_uris = _extract_data_uris(html, size_threshold=10000)
    if not data_uris:
        return html

    counter = {}
    for full_uri, mime_type, b64 in data_uris:
        try:
            content = base64.b64decode(b64)
            ext = _mime_to_ext(mime_type)
            counter[ext] = counter.get(ext, 0) + 1
            suffix = "" if counter[ext] == 1 else str(counter[ext])
            filename = f"asset_round{round_num}_{ext.replace('.', '')}{suffix}.{ext}"
            path = _upload_asset(repo, filename, content, message=f"Add {ext.upper()} asset for round {round_num}")
            html = html.replace(full_uri, path)
        except Exception:
            continue
    return html

