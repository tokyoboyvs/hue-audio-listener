from __future__ import annotations

from hue_audio_listener.api_client import HueApiClient
from hue_audio_listener.config import load_settings
import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="hue-audio-listener")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("health")

    toggle_parser = subparsers.add_parser("toggle")
    toggle_parser.add_argument("--light-id", dest="light_id")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    settings = load_settings()
    client = HueApiClient(
        base_url=settings.api_base_url,
        api_key=settings.api_key,
    )

    if args.command == "health":
        result = client.get_health()
        print(result)
        return 0
    
    if args.command == "toggle":
        light_id = args.light_id or settings.target_light_id
        if not light_id:
            parser.error("light id is required via --light-id or HUE_TARGET_LIGHT_ID")
        result = client.toggle_light(light_id)
        print(result)
        return 0
    
    parser.error("unknown command")
    return 1
