"""GitLab-адаптер (тонкий клиент MR API; merge_request_event в CI).

Токен: GITLAB_TOKEN (project access token, api: read/write для меток).
"""

from __future__ import annotations

import os
from urllib.parse import quote


class GitLabAdapter:
    def __init__(self, project_id: str, token: str | None = None, base_url: str = "https://gitlab.com/api/v4") -> None:
        self._project = quote(str(project_id), safe="")
        self._token = token or os.environ.get("GITLAB_TOKEN", "")
        self._base = base_url.rstrip("/")

    def _headers(self) -> dict[str, str]:
        return {"PRIVATE-TOKEN": self._token}

    def set_labels(self, pr_number: int, labels: list[str]) -> None:
        import requests

        url = f"{self._base}/projects/{self._project}/merge_requests/{pr_number}"
        requests.put(url, headers=self._headers(), json={"labels": ",".join(labels)}, timeout=30)

    def post_summary(self, pr_number: int, text_markdown: str) -> None:
        import requests

        url = f"{self._base}/projects/{self._project}/merge_requests/{pr_number}/notes"
        requests.post(url, headers=self._headers(), json={"body": text_markdown}, timeout=30)

    def list_review_logins(self, pr_number: int) -> list[str]:
        import requests

        url = f"{self._base}/projects/{self._project}/merge_requests/{pr_number}/approvals"
        resp = requests.get(url, headers=self._headers(), timeout=30)
        data = resp.json() if resp.ok else {}
        approved = data.get("approved_by", []) if isinstance(data, dict) else []
        return [str(a.get("user", {}).get("username", "")) for a in approved if isinstance(a, dict)]
