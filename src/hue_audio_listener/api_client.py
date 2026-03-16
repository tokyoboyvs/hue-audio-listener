from __future__ import annotations
import httpx


class HueApiClient:
    def __init__(self, base_url: str, api_key: str, timeout: float = 2.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._timeout = timeout

    def get_health(self) -> dict:
        response = httpx.get(
            f"{self._base_url}/health",
            timeout=self._timeout,
        )
        response.raise_for_status()
        return response.json()

    def toggle_light(self, light_id: str) -> dict:
        response = httpx.post(
            f"{self._base_url}/api/lights/{light_id}/toggle",
            headers=self.build_api_headers(),
            timeout=self._timeout,
        )
        response.raise_for_status()
        return response.json()
    
    def build_api_headers(self) -> dict[str, str]:
        return {
            "X-API-Key": self._api_key,
        }
