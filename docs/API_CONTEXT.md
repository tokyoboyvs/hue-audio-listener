# API_CONTEXT.md

## Scope

This document describes the real HTTP contract currently exposed by the `hue-local-api` repository, based on code inspection and test validation.

It is written for a separate client repository that must consume this API over HTTP and must not talk directly to the Philips Hue Bridge.

## Current Behavior

- Framework: FastAPI
- App title: `Hue Local API`
- Version: `0.1.0`
- Main API prefix: `/api`
- Public health route: `/health`
- Non-API UI route also exists: `/ui`
- Static assets are mounted under `/static`, but they are not part of the intended integration contract for an audio/voice client

## Probable Base URL

Most likely local URLs:

- `http://127.0.0.1:8000`
- `http://localhost:8000`
- `http://<local-machine-ip>:8000`

Why:
- `README.md` documents `127.0.0.1:8000`
- `run.py` defaults to port `8000`
- `docker-compose.yml` maps `8000:8000`

For a separate audio/voice client, treat the base URL as configurable.

## Authentication

### Current auth

All routes under `/api/...` require:

- header: `X-API-Key`
- value: must exactly match the server-side `API_KEY`

### Public route

- `GET /health` does not require authentication

### Current error behavior

If `X-API-Key` is missing or invalid:
- HTTP `401`
- body:
  `{"detail":"Invalid or missing API key"}`

If the server has no configured API key:
- HTTP `500`
- body:
  `{"detail":"API key is not configured"}`

## Headers

### Required on authenticated routes

- `X-API-Key: <your-api-key>`

### Common useful header

- `Content-Type: application/json` for POST requests with JSON body

No other custom client headers are required by current code.

## Data Models

### Light

```json
{
  "id": "light-1",
  "name": "Desk Lamp",
  "room": "office",
  "is_on": true,
  "brightness": 75,
  "color": "#FFD47A"
}
```

Fields:
- `id`: string
- `name`: string
- `room`: string
- `is_on`: boolean
- `brightness`: integer, `0..100`
- `color`: uppercase/lowercase hex string matching `^#[0-9A-Fa-f]{6}$`

### Room

```json
{
  "name": "office",
  "light_count": 1
}
```

Fields:
- `name`: string
- `light_count`: integer

## Endpoints

### `GET /health`

Public health endpoint.

Response `200`:
```json
{
  "status": "ok",
  "app": "hue-local-api",
  "version": "0.1.0",
  "mode": "mock"
}
```

Notes:
- `mode` is typically `mock` or `real`

---

### `GET /api/lights`

Returns all lights.

Auth:
- required

Response `200`:
```json
{
  "mode": "mock",
  "items": [
    {
      "id": "light-1",
      "name": "Desk Lamp",
      "room": "office",
      "is_on": true,
      "brightness": 75,
      "color": "#FFD47A"
    }
  ]
}
```

Possible errors:
- `401` invalid or missing API key
- `500` Hue Bridge not configured
- `502` Hue Bridge authentication failed
- `502` Hue Bridge is unreachable
- `404` Hue resource not found

Notes for client usage:
- In `mock` mode this is stable and test-covered
- In `real` mode, returned `color` is not reliable today; code currently maps color to `#FFFFFF`

---

### `GET /api/lights/bridge/status`

Returns API-side bridge status.

Auth:
- required

Response `200`:
```json
{
  "mode": "mock",
  "bridge_configured": false,
  "bridge_reachable": false
}
```

Notes:
- In `mock` mode it always returns `bridge_configured=false` and `bridge_reachable=false`
- In `real` mode it checks whether bridge credentials are present and whether a bridge call succeeds

Possible errors:
- `401` invalid or missing API key
- `500` Hue Bridge not configured
- `502` Hue Bridge authentication failed
- `502` Hue Bridge is unreachable
- `404` Hue resource not found

---

### `GET /api/lights/{light_id}`

Returns one light by ID.

Auth:
- required

Path params:
- `light_id`: string

Response `200`:
```json
{
  "mode": "mock",
  "item": {
    "id": "light-1",
    "name": "Desk Lamp",
    "room": "office",
    "is_on": true,
    "brightness": 75,
    "color": "#FFD47A"
  }
}
```

Possible errors:
- `401` invalid or missing API key
- `404` `{"detail":"Light '<light_id>' not found"}`
- `500` Hue Bridge not configured
- `502` Hue Bridge authentication failed
- `502` Hue Bridge is unreachable
- `404` `{"detail":"Hue resource not found"}` in some bridge-level cases

Notes:
- Not-found shape varies depending on where the failure occurs:
  - route-level not found: `Light '<id>' not found`
  - bridge-level not found: `Hue resource not found`

---

### `POST /api/lights/{light_id}/on`

Turns one light on.

Auth:
- required

Body:
- none

Response `200`:
```json
{
  "success": true,
  "message": "Light 'light-1' turned on",
  "light": {
    "id": "light-1",
    "name": "Desk Lamp",
    "room": "office",
    "is_on": true,
    "brightness": 75,
    "color": "#FFD47A"
  }
}
```

Possible errors:
- `401`
- `404`
- `500`
- `502`

---

### `POST /api/lights/{light_id}/off`

Turns one light off.

Auth:
- required

Body:
- none

Response `200`:
```json
{
  "success": true,
  "message": "Light 'light-1' turned off",
  "light": {
    "id": "light-1",
    "name": "Desk Lamp",
    "room": "office",
    "is_on": false,
    "brightness": 75,
    "color": "#FFD47A"
  }
}
```

Possible errors:
- `401`
- `404`
- `500`
- `502`

---

### `POST /api/lights/{light_id}/toggle`

Toggles one light.

Auth:
- required

Body:
- none

Response `200`:
```json
{
  "success": true,
  "message": "Light 'light-1' toggled",
  "light": {
    "id": "light-1",
    "name": "Desk Lamp",
    "room": "office",
    "is_on": false,
    "brightness": 75,
    "color": "#FFD47A"
  }
}
```

Possible errors:
- `401`
- `404`
- `500`
- `502`

Notes for clap client:
- this is the most natural endpoint for a “2 valid claps within 3 seconds” action

---

### `POST /api/lights/{light_id}/brightness`

Sets brightness for one light.

Auth:
- required

Body:
```json
{
  "brightness": 20
}
```

Validation:
- `brightness` is an integer from `0` to `100`

Response `200`:
```json
{
  "success": true,
  "message": "Light 'light-1' brightness set to 20",
  "light": {
    "id": "light-1",
    "name": "Desk Lamp",
    "room": "office",
    "is_on": true,
    "brightness": 20,
    "color": "#FFD47A"
  }
}
```

Possible errors:
- `401`
- `404`
- `422` invalid request body, for example brightness > 100
- `500`
- `502`

Notes for voice client:
- suitable for commands like `Philips luminosité 50%`

---

### `POST /api/lights/{light_id}/color`

Sets color for one light using a hex string.

Auth:
- required

Body:
```json
{
  "color": "#00FFAA"
}
```

Validation:
- `color` must match `^#[0-9A-Fa-f]{6}$`

Response `200`:
```json
{
  "success": true,
  "message": "Light 'light-1' color set to #00FFAA",
  "light": {
    "id": "light-1",
    "name": "Desk Lamp",
    "room": "office",
    "is_on": true,
    "brightness": 75,
    "color": "#00FFAA"
  }
}
```

Possible errors:
- `401`
- `404`
- `422` invalid hex color
- `500`
- `502`

Notes for voice client:
- suitable for commands like `Philips couleur rouge` after local mapping from color names to hex values

---

### `POST /api/lights/actions/on`

Bulk turn on.

Auth:
- required

Body:
```json
{
  "light_ids": ["light-1", "light-2"]
}
```

Validation:
- `light_ids` must contain at least one string item

Response `200`:
```json
{
  "success": true,
  "message": "Bulk on action executed",
  "updated_lights": [
    {
      "id": "light-1",
      "name": "Desk Lamp",
      "room": "office",
      "is_on": true,
      "brightness": 75,
      "color": "#FFD47A"
    }
  ],
  "missing_light_ids": []
}
```

Current reliability warning:
- works in `mock` mode
- not correctly implemented in `real` mode yet; the real client currently returns empty arrays

---

### `POST /api/lights/actions/off`

Bulk turn off.

Auth:
- required

Body:
```json
{
  "light_ids": ["light-1", "light-2"]
}
```

Response shape:
```json
{
  "success": true,
  "message": "Bulk off action executed",
  "updated_lights": [],
  "missing_light_ids": []
}
```

Current reliability warning:
- works in `mock` mode
- not correctly implemented in `real` mode yet

---

### `POST /api/lights/actions/toggle`

Bulk toggle.

Auth:
- required

Body:
```json
{
  "light_ids": ["light-1", "light-2"]
}
```

Response shape:
```json
{
  "success": true,
  "message": "Bulk toggle action executed",
  "updated_lights": [],
  "missing_light_ids": []
}
```

Current reliability warning:
- works in `mock` mode
- not correctly implemented in `real` mode yet

---

### `GET /api/rooms`

Returns rooms.

Auth:
- required

Response `200`:
```json
{
  "mode": "mock",
  "items": [
    {
      "name": "office",
      "light_count": 1
    },
    {
      "name": "bedroom",
      "light_count": 1
    }
  ]
}
```

Possible errors:
- `401`
- `500`
- `502`
- `404` bridge-level not found

---

### `GET /api/rooms/{room_name}/lights`

Returns lights belonging to one room.

Auth:
- required

Path params:
- `room_name`: string

Response `200`:
```json
{
  "mode": "mock",
  "items": [
    {
      "id": "light-1",
      "name": "Desk Lamp",
      "room": "office",
      "is_on": true,
      "brightness": 75,
      "color": "#FFD47A"
    }
  ]
}
```

Possible errors:
- `401`
- `404` `{"detail":"Room '<room_name>' not found"}`
- `500`
- `502`

Important behavior:
- current route returns `404` whenever no light is found for that room
- this means a truly empty room is indistinguishable from an unknown room

Case-sensitivity warning:
- in `mock` mode, room matching is case-sensitive
- in `real` mode, room matching is case-insensitive

## Validation Errors

FastAPI/Pydantic validation errors use the standard FastAPI shape.

Example `422` response:
```json
{
  "detail": [
    {
      "type": "less_than_equal",
      "loc": ["body", "brightness"],
      "msg": "Input should be less than or equal to 100",
      "input": 101,
      "ctx": {
        "le": 100
      }
    }
  ]
}
```

Do not hardcode exact validation message text if you can avoid it.
Only rely on:
- HTTP status `422`
- presence of `detail`

## Notes Useful For An Audio/Voice Client

### Good current fit

This API is already sufficient for:
- clap-driven single-light toggle
- simple voice commands on a known light ID
- setting a light brightness percentage
- setting a light color via a local color-name-to-hex mapping

### Recommended client strategy

For a separate audio/voice client:
1. call `GET /health` on startup if desired
2. call `GET /api/lights` to discover IDs
3. cache a mapping from spoken target names to `light_id`
4. use single-light routes for actual actions
5. treat bulk routes as experimental until the server-side real client is fixed

### Safe assumptions

You can safely assume today:
- `/api/...` requires `X-API-Key`
- brightness uses `0..100`
- color uses `#RRGGBB`
- successful action responses include an updated `light` object
- clap toggle should map naturally to `POST /api/lights/{light_id}/toggle`

### Unsafe assumptions

Do not assume:
- bulk routes behave correctly in real bridge mode
- `GET` light color is accurate in real bridge mode
- room lookup is normalized identically across modes
- the server exposes a dedicated voice/clap route
- the API returns structured machine-readable error codes beyond `detail`

## Current Behavior vs Recommended Future Usage

### Current behavior

Real endpoints available now:
- health
- list lights
- get one light
- one-light on/off/toggle
- one-light brightness update
- one-light color update
- bridge status
- list rooms
- list room lights
- bulk on/off/toggle

### Recommended future usage

For production-quality audio/voice integration, the API would benefit from:
- reliable bulk actions in real mode
- normalized room lookup behavior
- accurate color readback from the bridge
- optional endpoint(s) for name-based control instead of requiring a client-maintained ID mapping

## Suggested Future Endpoints

These do not currently exist. They are suggestions only.

### Name-based single target action

`POST /api/lights/by-name/{light_name}/toggle`

Useful because the audio/voice client often starts from spoken names, not stored IDs.

### Room-scoped action

`POST /api/rooms/{room_name}/actions/off`

Useful for commands like:
- `Philips éteins le salon`

### Intent-oriented endpoint

`POST /api/intents/light-command`

Example body:
```json
{
  "target_type": "light",
  "target": "desk lamp",
  "action": "set_brightness",
  "value": 50
}
```

This would move parsing complexity from the audio client to the API layer, but it does not exist today.

## Source Confidence

This document was derived from:
- FastAPI route definitions
- Pydantic request/response models
- service implementation
- test suite
- local test execution with all tests passing

Where implementation gaps exist, they are marked explicitly above.
