from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from hue_audio_listener import cli


def test_main_health_calls_client(monkeypatch, capsys):
    class FakeClient:
        def get_health(self):
            return {"status": "ok"}

    monkeypatch.setattr(
        cli,
        "load_settings",
        lambda: type(
            "Settings",
            (),
            {
                "api_base_url": "http://127.0.0.1:8000",
                "api_key": "D83G32sKsKGJWfnFkbGF3uOodMJzABROpmLst25KJxxdQxM3mIuac62BQp6XJ7UaiSi3tONWxrBkqjdwHsPGrU967dG2JUEDh012Kv0CPYVzDaZmYExH96BoeFzlouatVfSDdnMceuX4kPdIO7ldHGYjyvur0rM88nq8nEDHqeFTRTCENLfnRHaHLENy2a2XSA2OBHZbn9Qlwpc06FLTAWacfiWMN3l8Huu5AVHAloJIJDqVG9irafvjqPWHEMog",
                "target_light_id": "",
            },
        )(),
    )
    monkeypatch.setattr(cli, "HueApiClient", lambda **kwargs: FakeClient())
    monkeypatch.setattr(sys, "argv", ["hue-audio-listener", "health"])

    exit_code = cli.main()
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "{'status': 'ok'}" in output


def test_main_toggle_uses_config_light_id(monkeypatch, capsys):
    class FakeClient:
        def toggle_light(self, light_id: str):
            return {"status": "ok", "light_id": light_id}

    monkeypatch.setattr(
        cli,
        "load_settings",
        lambda: type(
            "Settings",
            (),
            {
                "api_base_url": "http://127.0.0.1:8000",
                "api_key": "D83G32sKsKGJWfnFkbGF3uOodMJzABROpmLst25KJxxdQxM3mIuac62BQp6XJ7UaiSi3tONWxrBkqjdwHsPGrU967dG2JUEDh012Kv0CPYVzDaZmYExH96BoeFzlouatVfSDdnMceuX4kPdIO7ldHGYjyvur0rM88nq8nEDHqeFTRTCENLfnRHaHLENy2a2XSA2OBHZbn9Qlwpc06FLTAWacfiWMN3l8Huu5AVHAloJIJDqVG9irafvjqPWHEMog",
                "target_light_id": "light-123",
            },
        )(),
    )
    monkeypatch.setattr(cli, "HueApiClient", lambda **kwargs: FakeClient())
    monkeypatch.setattr(sys, "argv", ["hue-audio-listener", "toggle"])

    exit_code = cli.main()
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "light-123" in output
