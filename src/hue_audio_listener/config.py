from __future__ import annotations
from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    api_base_url: str
    api_key: str
    target_light_id: str
    clap_window_seconds: float
    clap_cooldown_seconds: float


def load_settings() -> Settings:
    return Settings(
        api_base_url=os.getenv("HUE_API_BASE_URL", "http://127.0.0.1:8000"),
        api_key=os.getenv("HUE_API_KEY", ""),
        target_light_id=os.getenv("HUE_TARGET_LIGHT_ID", ""),
        clap_window_seconds=float(os.getenv("CLAP_WINDOW_SECONDS", "3.0")),
        clap_cooldown_seconds=float(os.getenv("CLAP_COOLDOWN_SECONDS", "5.0")),
    )
