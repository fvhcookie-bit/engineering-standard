"""GitHub-адаптер (тонкий клиент REST, токен из окружения — GITHUB_TOKEN).

Скоуп токена: pull-requests: write (labels/comments), contents: read.
Сетевые вызовы в юнит-тестах не выполняются — только FakeAdapter.
"""

from __future__ import annotations

import os


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
