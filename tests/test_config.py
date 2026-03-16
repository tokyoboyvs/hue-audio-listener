from hue_audio_listener.config import load_settings


def test_load_settings_uses_defaults(monkeypatch):
    monkeypatch.delenv("HUE_API_BASE_URL", raising=False)
    monkeypatch.delenv("HUE_API_KEY", raising=False)
    monkeypatch.delenv("HUE_TARGET_LIGHT_ID", raising=False)
    monkeypatch.delenv("CLAP_WINDOW_SECONDS", raising=False)
    monkeypatch.delenv("CLAP_COOLDOWN_SECONDS", raising=False)

    settings = load_settings()

    assert settings.api_base_url == "http://127.0.0.1:8000"
    assert settings.api_key == ""
    assert settings.target_light_id == ""
    assert settings.clap_window_seconds == 3.0
    assert settings.clap_cooldown_seconds == 5.0


def test_load_settings_reads_environment(monkeypatch):
    monkeypatch.setenv("HUE_API_BASE_URL", "http://192.168.1.50:8000")
    monkeypatch.setenv("HUE_API_KEY", "D83G32sKsKGJWfnFkbGF3uOodMJzABROpmLst25KJxxdQxM3mIuac62BQp6XJ7UaiSi3tONWxrBkqjdwHsPGrU967dG2JUEDh012Kv0CPYVzDaZmYExH96BoeFzlouatVfSDdnMceuX4kPdIO7ldHGYjyvur0rM88nq8nEDHqeFTRTCENLfnRHaHLENy2a2XSA2OBHZbn9Qlwpc06FLTAWacfiWMN3l8Huu5AVHAloJIJDqVG9irafvjqPWHEMog")
    monkeypatch.setenv("HUE_TARGET_LIGHT_ID", "light-1")
    monkeypatch.setenv("CLAP_WINDOW_SECONDS", "2.5")
    monkeypatch.setenv("CLAP_COOLDOWN_SECONDS", "8.0")

    settings = load_settings()

    assert settings.api_base_url == "http://192.168.1.50:8000"
    assert settings.api_key == "D83G32sKsKGJWfnFkbGF3uOodMJzABROpmLst25KJxxdQxM3mIuac62BQp6XJ7UaiSi3tONWxrBkqjdwHsPGrU967dG2JUEDh012Kv0CPYVzDaZmYExH96BoeFzlouatVfSDdnMceuX4kPdIO7ldHGYjyvur0rM88nq8nEDHqeFTRTCENLfnRHaHLENy2a2XSA2OBHZbn9Qlwpc06FLTAWacfiWMN3l8Huu5AVHAloJIJDqVG9irafvjqPWHEMog"
    assert settings.target_light_id == "light-1"
    assert settings.clap_window_seconds == 2.5
    assert settings.clap_cooldown_seconds == 8.0
