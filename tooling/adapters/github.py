"""GitHub-адаптер (тонкий клиент REST, токен из окружения — GITHUB_TOKEN).

Скоуп токена: pull-requests: write (labels/comments), contents: read.
Сетевые вызовы в юнит-тестах не выполняются — только FakeAdapter.
"""

from __future__ import annotations

import os
from typing import Any


class GitHubAdapter:
    def __init__(self, repo: str, token: str | None = None, base_url: str = "https://api.github.com") -> None:
        self._repo = repo
        self._token = token or os.environ.get("GITHUB_TOKEN", "")
        self._base = base_url.rstrip("/")

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._token}",
            "Accept": "application/vnd.github+json",
        }

    def set_labels(self, pr_number: int, labels: list[str]) -> None:
        import requests

        url = f"{self._base}/repos/{self._repo}/issues/{pr_number}/labels"
        requests.put(url, headers=self._headers(), json={"labels": labels}, timeout=30)

    def post_summary(self, pr_number: int, text_markdown: str) -> None:
        import requests

        url = f"{self._base}/repos/{self._repo}/issues/{pr_number}/comments"
        requests.post(url, headers=self._headers(), json={"body": text_markdown}, timeout=30)

    def list_review_logins(self, pr_number: int) -> list[str]:
        import requests

        url = f"{self._base}/repos/{self._repo}/pulls/{pr_number}/reviews"
        resp = requests.get(url, headers=self._headers(), timeout=30)
        data = resp.json() if resp.ok else []
        return [str(r.get("user", {}).get("login", "")) for r in data if isinstance(r, dict)]

    def get_branch_protection(self, branch: str) -> dict[str, Any] | None:
        import requests

        from adapters.base import AdapterUnavailable

        url = f"{self._base}/repos/{self._repo}/branches/{branch}/protection"
        resp = requests.get(url, headers=self._headers(), timeout=30)
        if resp.status_code == 404:
            return None  # не защищена (или нет прав админа — см. README гейта)
        if not resp.ok:
            raise AdapterUnavailable(f"GitHub API: {resp.status_code}")
        return dict(resp.json())

    def get_codeowners(self) -> str | None:
        import base64

        import requests

        from adapters.base import AdapterUnavailable

        for path in (".github/CODEOWNERS", "CODEOWNERS", "docs/CODEOWNERS"):
            url = f"{self._base}/repos/{self._repo}/contents/{path}"
            resp = requests.get(url, headers=self._headers(), timeout=30)
            if resp.status_code == 404:
                continue
            if not resp.ok:
                raise AdapterUnavailable(f"GitHub API: {resp.status_code}")
            data = resp.json()
            return base64.b64decode(data.get("content", "")).decode("utf-8")
        return None

    def get_commit_check_status(self, commit_sha: str) -> str | None:
        import requests

        from adapters.base import AdapterUnavailable

        url = f"{self._base}/repos/{self._repo}/commits/{commit_sha}/status"
        resp = requests.get(url, headers=self._headers(), timeout=30)
        if not resp.ok:
            raise AdapterUnavailable(f"GitHub API: {resp.status_code}")
        state = resp.json().get("state")
        return str(state) if state else None

    def run_belongs_to_commit(self, run_id: int, commit_sha: str) -> bool:
        import requests

        from adapters.base import AdapterUnavailable

        url = f"{self._base}/repos/{self._repo}/actions/runs/{run_id}"
        resp = requests.get(url, headers=self._headers(), timeout=30)
        if not resp.ok:
            raise AdapterUnavailable(f"GitHub API: {resp.status_code}")
        return str(resp.json().get("head_sha", "")) == commit_sha

    def get_task_files(self, task_id: str) -> list[str] | None:
        from adapters.base import AdapterUnavailable

        raise AdapterUnavailable(f"трекер задач не подключён (task {task_id})")
