# LabPocket

**A phone-friendly MicroPython helper for ECE labs on slow or crowded Wi-Fi.**

Project code: **B-CODE-06** · Repository:
[sandhiyaL12/Lab-Pocket](https://github.com/sandhiyaL12/Lab-Pocket)

LabPocket is for ECE students and instructors learning MicroPython on ESP32
and Raspberry Pi Pico (RP2) boards. It provides a small API for board-selected
questions, with compressed JSON, plain-text answers, and server-sent streaming.

## What is in this project now

- FastAPI endpoints: `/health`, `/chat`, `/chat/stream`, and `/usage`.
- Board input validation for ESP32 and Pico/RP2 aliases.
- OpenAI-compatible primary and fallback LLM providers, timeouts, retries,
  token/cost logging, and configurable prices.
- GZip compression for HTTP responses and `POST /chat?text_only=true`.
- Dockerfile, Docker Compose API + pgvector/PostgreSQL services, and CI tests.
- MicroPython `v1.29.0` source corpus collected under `data/raw/` (kept out of
  Git) and a small sample under `data/sample/`.
- Ten real lab questions with source-file references in [docs/QUESTIONS.md](docs/QUESTIONS.md).

## Important current limitation

The source corpus is collected but is **not yet indexed or connected to the
chat endpoint**. The LLM answers are not source-verified and do not yet include
citations. Source retrieval, per-port filtering of evidence, fact-checking, and
comparison tables are the next project phase. Do not treat generated answers
as verified MicroPython documentation.

Responses are capped below 5 KB (including oversized answers, which are marked
as shortened) and the limit is covered by local tests. The under-3-second
first-token goal has not yet been measured on a throttled 2G-like link, and
this repository does not currently have a verified live-host URL.

## Run locally

Requires Python 3.11+.

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
```

Set `PRIMARY_API_KEY` in `.env` to a key for an OpenAI-compatible endpoint. The
fallback is optional; configure its key, URL, and model to enable it. Set the
cost-per-million-token values to the current provider prices or `/usage` will
report a zero estimate.

```powershell
uvicorn app.main:app --reload
```

The API is available at `http://127.0.0.1:8000`; interactive API documentation
is at `/docs`.

## Run with Docker Compose

The Compose file starts both the API and a pgvector-enabled PostgreSQL service.
The API does not use the database yet; it is provisioned for a later retrieval
phase. The default database password is for local development only.

```powershell
docker compose -f docker_compose.yml up --build
```

Set secrets through `.env`; do not commit that file. Check liveness at
`http://localhost:8000/health`.

## Example requests

Structured JSON:

```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:8000/chat `
  -ContentType 'application/json' `
  -Body '{"board":"ESP32","question":"How does machine.Pin work?"}'
```

Plain text:

```powershell
Invoke-WebRequest -Method Post -Uri 'http://localhost:8000/chat?text_only=true' `
  -ContentType 'application/json' `
  -Body '{"board":"Pico","question":"How do I use hardware PWM?"}'
```

Streaming clients can `POST` the same JSON body to `/chat/stream` and consume
SSE `token`, `done`, and `error` events. `/usage` reports logged requests,
tokens, and cost based on configured prices.

## Checks

```powershell
ruff check app tests
python -m pytest -q
docker compose -f docker_compose.yml config -q
pre-commit run --all-files
```

## Dataset and licensing

MicroPython source is from the upstream
[MicroPython repository](https://github.com/micropython/micropython) and is
distributed under the MIT license. Keep upstream notices when using or
redistributing its source. Dataset paths and scope are documented in
[DATASET.md](DATASET.md); system endpoints and response shapes are in
[DESIGN.md](DESIGN.md).
