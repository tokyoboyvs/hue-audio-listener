from __future__ import annotations

from hue_audio_listener.clap_detector import ClapDetector
from hue_audio_listener.api_client import HueApiClient
from hue_audio_listener.config import load_settings
import argparse
import httpx


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="hue-audio-listener")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("health")

    toggle_parser = subparsers.add_parser("toggle")
    toggle_parser.add_argument("--light-id", dest="light_id")

    simulate_parser = subparsers.add_parser("simulate-claps")
    simulate_parser.add_argument("timestamps", nargs="+", type=float)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    settings = load_settings()
    client = HueApiClient(
        base_url=settings.api_base_url,
        api_key=settings.api_key,
    )

    try: 
        if args.command == "health":
            result = client.get_health()
            print(result)
            return 0
        
        if args.command == "toggle":
            light_id = args.light_id or settings.target_light_id
            if not light_id:
                print("Error: light id is required via --light-id or HUE_TARGET_LIGHT_ID")
                return 2
            
            result = client.toggle_light(light_id)
            print(result)
            return 0

        if args.command == "simulate-claps":
            detector = ClapDetector(
                max_interval_seconds=settings.clap_window_seconds,
                cooldown_seconds=settings.clap_cooldown_seconds,
            )

            triggered_at = []

            for timestamp in args.timestamps:
                if detector.process_peak(timestamp):
                    triggered_at.append(timestamp)
            
            print({"triggered_at": triggered_at})
            return 0

        print("Error: unknown command")
        return 2
    
    except httpx.HTTPStatusError as exc:
        status_code = exc.response.status_code

        if status_code == 401:
            print("Error: unauthorized. Check HUE_API_KEY.")
            return 1
        
        print(f"Error: API request failed with status {status_code}.")
        return 1
    
    except httpx.HTTPError as exc:
        print(f"Error: request failed: {exc}")
        return 1
