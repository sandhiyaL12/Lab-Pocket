import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def log_call(
    log_path: str | Path,
    *,
    provider: str,
    model: str,
    usage: dict[str, Any],
    latency_ms: float,
    price_in_per_m: float,
    price_out_per_m: float,
    ok: bool,
    fallback_used: bool = False,
) -> dict[str, Any]:
    input_tokens = usage.get("input_tokens", 0)
    output_tokens = usage.get("output_tokens", 0)
    estimated = usage.get("estimated", False)

    input_tokens = int(input_tokens or 0)
    output_tokens = int(output_tokens or 0)

    cost_input = input_tokens * price_in_per_m / 1000000
    cost_output = output_tokens * price_out_per_m / 1000000

    record = {
        "timestamp": datetime.now(UTC).isoformat(),
        "provider": provider,
        "model": model,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens,
        "cost_usd": round(cost_input + cost_output, 10),
        "latency_ms": round(latency_ms, 2),
        "ok": ok,
        "fallback_used": fallback_used,
        "estimated": estimated,
    }

    path = Path(log_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("a", encoding="utf-8", newline="\n") as file:
        file.write(json.dumps(record) + "\n")

    return record
