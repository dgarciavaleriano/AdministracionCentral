# ACFrontEnd/services/api/client.py
from __future__ import annotations
from typing import Any, Optional
import requests


class ApiClient:
    def __init__(self, base_url: str, timeout: float = 10.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})

    def _url(self, path: str) -> str:
        if not path.startswith("/"):
            path = f"/{path}"
        return f"{self.base_url}{path}"

    def get(self, path: str, params: Optional[dict[str, Any]] = None) -> Any:
        response = self.session.get(self._url(path), params=params, timeout=self.timeout)
        response.raise_for_status()
        content_type = response.headers.get("content-type", "")
        if "application/json" in content_type:
            return response.json()
        return response.text

    def post(self, path: str, json: Optional[dict[str, Any]] = None) -> Any:
        response = self.session.post(self._url(path), json=json, timeout=self.timeout)
        response.raise_for_status()
        content_type = response.headers.get("content-type", "")
        if "application/json" in content_type:
            return response.json()
        return response.text

    def close(self) -> None:
        self.session.close()