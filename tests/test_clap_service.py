from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from hue_audio_listener.clap_detector import ClapDetector
from hue_audio_listener.clap_service import ClapService


class FakeApiClient:
    def __init__(self) -> None:
        self.toggled_light_ids: list[str] = []

    def toggle_light(self, light_id: str) -> dict:
        self.toggled_light_ids.append(light_id)
        return {"status": "ok", "light_id": light_id}


def test_process_peak_does_not_toggle_before_double_clap():
    api_client = FakeApiClient()
    service = ClapService(
        detector=ClapDetector(),
        api_client=api_client,
        target_light_id="light-1",
    )

    result = service.process_peak(1.0)

    assert result is False
    assert api_client.toggled_light_ids == []


def test_process_peak_toggles_once_when_double_clap_is_detected():
    api_client = FakeApiClient()
    service = ClapService(
        detector=ClapDetector(),
        api_client=api_client,
        target_light_id="light-1",
    )

    first_result = service.process_peak(1.0)
    second_result = service.process_peak(1.4)

    assert first_result is False
    assert second_result is True
    assert api_client.toggled_light_ids == ["light-1"]


def test_process_peak_respects_detector_cooldown():
    api_client = FakeApiClient()
    service = ClapService(
        detector=ClapDetector(cooldown_seconds=5.0),
        api_client=api_client,
        target_light_id="light-1",
    )

    assert service.process_peak(1.0) is False
    assert service.process_peak(1.4) is True
    assert service.process_peak(2.0) is False
    assert service.process_peak(2.4) is False
    assert api_client.toggled_light_ids == ["light-1"]
