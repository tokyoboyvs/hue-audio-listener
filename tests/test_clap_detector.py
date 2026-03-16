from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from hue_audio_listener.clap_detector import ClapDetector


def test_single_peak_does_not_trigger():
    detector = ClapDetector()

    assert detector.process_peak(1.0) is False


def test_two_valid_peaks_trigger_double_clap():
    detector = ClapDetector()

    assert detector.process_peak(1.0) is False
    assert detector.process_peak(1.5) is True


def test_duplicate_peak_is_ignored_when_too_close():
    detector = ClapDetector(min_separation_seconds=0.15)

    assert detector.process_peak(1.0) is False
    assert detector.process_peak(1.05) is False
    assert detector.process_peak(1.4) is True


def test_second_peak_outside_window_restarts_sequence():
    detector = ClapDetector(max_interval_seconds=3.0)

    assert detector.process_peak(1.0) is False
    assert detector.process_peak(4.5) is False
    assert detector.process_peak(5.0) is True


def test_detector_ignores_peaks_during_cooldown():
    detector = ClapDetector(cooldown_seconds=5.0)

    assert detector.process_peak(1.0) is False
    assert detector.process_peak(1.4) is True
    assert detector.process_peak(2.0) is False
    assert detector.process_peak(2.5) is False
    assert detector.process_peak(6.6) is False
    assert detector.process_peak(7.0) is True
