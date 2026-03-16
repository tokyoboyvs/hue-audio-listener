from __future__ import annotations

from hue_audio_listener.clap_detector import ClapDetector
from hue_audio_listener.api_client import HueApiClient


class ClapService:
    def __init__(
            self,
            detector: ClapDetector,
            api_client: HueApiClient,
            target_light_id: str,
    ) -> None:
        self._detector = detector
        self._api_client = api_client
        self._target_light_id = target_light_id
    
    def process_peak(self, timestamp: float) -> bool:
        triggered = self._detector.process_peak(timestamp)

        if not triggered:
            return False
        
        self._api_client.toggle_light(self._target_light_id)
        return True
