# LabPocket API and system design

## Current architecture

- **API:** FastAPI (`app/main.py`).
- **LLM:** OpenAI-compatible chat-completions API with a configured primary
  provider, one fallback, request timeouts, and transient-error retries.
- **Board selection:** request validation normalizes ESP32 and Pico/RP2 names
  before they are included in the LLM prompt.
- **Responses:** compact JSON for `/chat`, plain text with `?text_only=true`,
  and server-sent events (SSE) from `/chat/stream`. GZip is enabled for
  compressible HTTP responses.
- **Usage:** append-only JSONL cost records and an aggregate `/usage` endpoint.
- **Local services:** Docker Compose starts the API and a pgvector-enabled
  PostgreSQL service. The application does not connect to that database yet.
- **Payload budget:** JSON and SSE responses are kept below 5 KB; oversized
  answers are explicitly marked as shortened.

The MicroPython corpus is collected locally, but retrieval, port-file filtering,
citations, and claim fact-checking are not implemented in this phase. The system
must not describe LLM output as source-verified.

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/` | API welcome response |
| `GET` | `/health` | Liveness and environment |
| `POST` | `/chat` | Board-validated question; returns structured JSON |
| `POST` | `/chat?text_only=true` | Same answer as `text/plain` |
| `POST` | `/chat/stream` | SSE `token`, `done`, and `error` events |
| `GET` | `/usage` | Request, token, and configured-price cost totals |

### Chat request

```json
{
  "board": "ESP32",
  "question": "How does machine.Pin work?"
}
```

Supported `board` values include `ESP32`, `Raspberry Pi Pico`, `Pico`, `RP2`,
and `RP2040`. Other values return HTTP 422.

### Chat response

```json
{
  "board": "ESP32",
  "answer": "…",
  "model_used": "…",
  "input_tokens": 0,
  "output_tokens": 0,
  "total_tokens": 0
}
```

An unconfigured or failed set of providers returns HTTP 502. The streaming route
reports errors as an SSE `error` event if the response has already started.
Retries and fallback are attempted before any streamed answer text is sent; if
a provider fails after emitting text, the stream ends with an error event
instead of switching providers and duplicating part of the answer.

## Configuration and usage accounting

Copy `.env.example` to `.env`. Provider prices are configurable in USD per
million tokens; totals are estimates based on those configured values and
provider-reported token counts. If no prices are set, the cost total is zero
and is not a provider invoice.

`/usage` reads `COST_LOG_PATH` (default `data/cost_log.jsonl`). The file is
append-only JSONL; keep it on persistent storage when deploying.

## Low-bandwidth validation

JSON compression, text-only responses, and streaming are implemented. The
under-5-KB response budget is enforced and tested locally. The under-3-second
first-token target still needs to be measured against a deployed provider under
a throttled 2G-like link; no such measurement or live-host URL is recorded yet.
