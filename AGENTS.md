# AGENTS.md

## Purpose

This repository is the future audio/voice client for Philips Hue control.

It is intentionally separate from the `hue-local-api` repository.

This project must:
- detect clap events from a microphone
- later support simple speech recognition
- call the existing local HTTP API exposed by `hue-local-api`

This project must not:
- talk directly to a Philips Hue Bridge
- contain Hue Bridge pairing logic
- store or use `HUE_BRIDGE_IP`
- store or use `HUE_APP_KEY`
- reimplement Hue device discovery or low-level Hue HTTP calls

The Hue-specific bridge logic belongs only in `hue-local-api`.
This repository is only an API client plus audio/voice logic.

## Read First

Before making changes, read these files in this repository:
1. `docs/API_CONTEXT.md`
2. `openapi.yaml`
3. `examples.http`
4. `.env.example`

Treat those files as the source of truth for how to call `hue-local-api`.

## System Boundary

Architecture boundary is strict:

- This repo:
  - microphone input
  - clap detection
  - voice parsing / speech recognition
  - intent extraction
  - HTTP requests to `hue-local-api`
  - retry / debounce / rate limiting on the client side if needed

- `hue-local-api`:
  - Philips Hue bridge communication
  - room/light discovery
  - light state changes
  - Hue bridge credentials and bridge-specific behavior

If you need a new lighting capability, prefer requesting or documenting a new API endpoint in `hue-local-api` instead of bypassing the API.

## Current API Assumptions

The current API is a local FastAPI service, typically reachable at:
- `http://127.0.0.1:8000`
- or another LAN/local-machine URL configured via environment variables

Current auth model:
- all `/api/...` routes require header `X-API-Key`
- `/health` is public

Current notable real-world limitations of `hue-local-api`:
- bulk light actions exist but are not reliable in real bridge mode yet
- light color reads are not reliable in real bridge mode yet
- room-light lookup behavior is not fully normalized across mock vs real mode

Because of those limitations:
- do not assume bulk routes are production-safe
- prefer single-light actions unless documentation explicitly says otherwise
- do not depend on `GET` responses for exact live color state in real mode

## Expected Behavior For This Repo

### Clap control

Initial target behavior:
- detect valid clap events from microphone input
- if 2 valid claps are detected within a 3 second maximum window, trigger a light toggle API call

Recommended behavior:
- use a short rolling event window
- ignore obvious duplicate peaks from the same clap
- require a minimum separation between accepted claps
- reject sustained noise, speech bursts, and clipping artifacts when possible
- avoid repeated toggles from one noisy sequence
- add a cooldown after a successful trigger

Default product behavior should be conservative:
- false positives are worse than missing a few claps

### Voice control

Planned command style:
- `Philips couleur rouge`
- `Philips luminosité 50%`
- `Philips éteins`

Recommended interpretation flow:
1. capture audio
2. run speech recognition
3. normalize French text
4. extract intent and parameters
5. call `hue-local-api`
6. return a clear success/failure result

If utterance parsing is ambiguous:
- fail safely
- do not send guessed destructive actions
- prefer asking for clarification when the product UX allows it

## API Usage Rules

When adding integrations:
- always use the configured base URL
- always send `X-API-Key` for `/api/...` calls
- use JSON bodies exactly as documented
- treat non-2xx responses as real failures
- log request intent and HTTP status without leaking secrets
- keep request timeouts short because the API is local

Preferred usage today:
- health check with `GET /health`
- enumerate lights with `GET /api/lights`
- control one light with:
  - `POST /api/lights/{light_id}/toggle`
  - `POST /api/lights/{light_id}/on`
  - `POST /api/lights/{light_id}/off`
  - `POST /api/lights/{light_id}/brightness`
  - `POST /api/lights/{light_id}/color`

## Things Not To Do

Do not:
- add direct Philips Hue Bridge calls in this repo
- add bridge credentials here
- copy code from `hue-local-api` for Hue control
- assume bulk endpoints are safe in real mode without verifying current server behavior
- assume room matching is perfectly normalized
- assume current color reads are accurate in real mode
- hardcode the API key
- hardcode light IDs unless explicitly intended for a local prototype
- invent undocumented API routes as if they already exist

## Current Behavior vs Recommended Future Usage

Current behavior:
- the API is enough to support clap-based toggling and simple single-light voice commands
- the API already supports on/off/toggle/brightness/color for a known light ID

Recommended future usage:
- maintain a local mapping layer from spoken command to target light ID or room strategy
- if room or group semantics become important, extend `hue-local-api` rather than bypassing it
- add stronger API contracts in `hue-local-api` before relying on bulk actions for production use

## Implementation Guidance For Codex

When working in this repo:
- start from the documented API contract, not assumptions
- prefer small adapters:
  - `audio capture`
  - `clap detector`
  - `speech recognizer`
  - `intent parser`
  - `hue-local-api client`
- keep the HTTP client isolated so it can be tested independently
- add fixture-based tests that mock `hue-local-api` responses
- document every assumption that depends on current API limitations

If behavior needed by this repo is missing from the API, add it to a section named `Suggested future endpoints` in local docs instead of pretending it already exists.
