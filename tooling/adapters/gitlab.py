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

    def get_commit_check_status(self, commit_sha: str) -> str | None:
        import requests

        from adapters.base import AdapterUnavailable

        url = f"{self._base}/projects/{self._project}/repository/commits/{commit_sha}/status"
        resp = requests.get(url, headers=self._headers(), timeout=30)
        if not resp.ok:
            raise AdapterUnavailable(f"GitLab API: {resp.status_code}")
        state = resp.json().get("status") if isinstance(resp.json(), dict) else None
        return str(state) if state else None

    def run_belongs_to_commit(self, run_id: int, commit_sha: str) -> bool:
        from adapters.base import AdapterUnavailable

        raise AdapterUnavailable("принадлежность прогонов в GitLab не поддерживается в v0.x")

    def get_task_files(self, task_id: str) -> list[str] | None:
        from adapters.base import AdapterUnavailable

        raise AdapterUnavailable(f"трекер задач не подключён (task {task_id})")
