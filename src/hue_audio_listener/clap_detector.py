from __future__ import annotations


class ClapDetector:
    def __init__(
            self,
            min_separation_seconds: float = 0.15,
            max_interval_seconds: float = 3.0,
            cooldown_seconds: float = 5.0,
    ) -> None:
        self._min_separation_seconds = min_separation_seconds
        self._max_interval_seconds = max_interval_seconds
        self._cooldown_seconds = cooldown_seconds
        self._first_clap_at: float | None = None
        self._last_peak_at: float | None = None
        self._cooldown_until: float = 0.0

    def process_peak(self, timestamp: float) -> bool:
        if timestamp < self._cooldown_until:
            return False
        
        if self._last_peak_at is not None:
            if timestamp - self._last_peak_at < self._min_separation_seconds:
                return False
            
        self._last_peak_at = timestamp

        if self._first_clap_at is None:
            self._first_clap_at = timestamp
            return False
        
        interval = timestamp - self._first_clap_at

        if interval > self._max_interval_seconds:
            self._first_clap_at = timestamp
            return False
        
        self._first_clap_at = None
        self._cooldown_until = timestamp + self._cooldown_seconds
        return True
