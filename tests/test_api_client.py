from pathlib import Path
import pytest
import httpx
import respx
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from hue_audio_listener.api_client import HueApiClient


@respx.mock
def test_get_health_returns_json():
    route = respx.get("http://127.0.0.1:8000/health").mock(
        return_value=httpx.Response(
            200,
            json={"status": "ok"},
        )
    )

    client = HueApiClient(
        base_url="http://127.0.0.1:8000",
        api_key="D83G32sKsKGJWfnFkbGF3uOodMJzABROpmLst25KJxxdQxM3mIuac62BQp6XJ7UaiSi3tONWxrBkqjdwHsPGrU967dG2JUEDh012Kv0CPYVzDaZmYExH96BoeFzlouatVfSDdnMceuX4kPdIO7ldHGYjyvur0rM88nq8nEDHqeFTRTCENLfnRHaHLENy2a2XSA2OBHZbn9Qlwpc06FLTAWacfiWMN3l8Huu5AVHAloJIJDqVG9irafvjqPWHEMog",
    )

    result = client.get_health()

    assert route.called
    assert result == {"status": "ok"}


@respx.mock
def test_get_health_raises_for_http_error():
    respx.get("http://127.0.0.1:8000/health").mock(
        return_value=httpx.Response(503, json={"detail": "unavailable"})
    )

    client = HueApiClient(
        base_url="http://127.0.0.1:8000",
        api_key="D83G32sKsKGJWfnFkbGF3uOodMJzABROpmLst25KJxxdQxM3mIuac62BQp6XJ7UaiSi3tONWxrBkqjdwHsPGrU967dG2JUEDh012Kv0CPYVzDaZmYExH96BoeFzlouatVfSDdnMceuX4kPdIO7ldHGYjyvur0rM88nq8nEDHqeFTRTCENLfnRHaHLENy2a2XSA2OBHZbn9Qlwpc06FLTAWacfiWMN3l8Huu5AVHAloJIJDqVG9irafvjqPWHEMog",
    )

    with pytest.raises(httpx.HTTPStatusError):
        client.get_health()


@respx.mock
def test_toggle_light_sends_api_key_header():
    route = respx.post("http://127.0.0.1:8000/api/lights/light-123/toggle").mock(
        return_value=httpx.Response(
            200,
            json={"status": "ok", "light_id": "light-123"},
        )
    )

    client = HueApiClient(
        base_url="http://127.0.0.1:8000",
        api_key="secret-key",
    )

    result = client.toggle_light("light-123")

    assert route.called
    request = route.calls[0].request
    assert request.headers["X-API-Key"] == "secret-key"
    assert result == {"status": "ok", "light_id": "light-123"}


@respx.mock
def test_toggle_light_raises_for_http_error():
    respx.post("http://127.0.0.1:8000/api/lights/light-123/toggle").mock(
        return_value=httpx.Response(401, json={"detail": "unauthorized"})
    )

    client = HueApiClient(
        base_url="http://127.0.0.1:8000",
        api_key="bad-key",
    )

    with pytest.raises(httpx.HTTPStatusError):
        client.toggle_light("light-123")

