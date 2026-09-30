from __future__ import annotations

import json
from pathlib import Path
from typing import Any

LOG_PATH = Path("data/logs.jsonl")


def percentile(values: list[float | int], p: int) -> float:
    if not values:
        return 0.0
    items = sorted(values)
    idx = max(0, min(len(items) - 1, round((p / 100) * len(items) + 0.5) - 1))
    return float(items[idx])


def compute_dashboard_metrics() -> dict[str, Any]:
    if not LOG_PATH.exists():
        return {"error": "data/logs.jsonl not found"}

    records: list[dict[str, Any]] = []
    for line in LOG_PATH.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except Exception:
            continue

    requests_received = [r for r in records if r.get("event") == "request_received"]
    requests_failed = [r for r in records if r.get("event") == "request_failed"]
    responses_sent = [r for r in records if r.get("event") == "response_sent"]

    # Latency
    latencies = [r["latency_ms"] for r in responses_sent if "latency_ms" in r]
    ttfts = [r["ttft_ms"] for r in responses_sent if "ttft_ms" in r]
    p50 = percentile(latencies, 50)
    p95 = percentile(latencies, 95)
    p99 = percentile(latencies, 99)
    ttft_p95 = percentile(ttfts, 95)

    # Traffic
    traffic_count = len(requests_received)
    # Rate per minute approximation over last 60m window
    traffic_rate_pm = traffic_count

    # Errors
    err_count = len(requests_failed)
    total_reqs = traffic_count if traffic_count > 0 else 1
    error_rate_pct = round((err_count / total_reqs) * 100, 2)
    error_breakdown: dict[str, int] = {}
    for r in requests_failed:
        etype = str(r.get("error_type", "Unknown"))
        error_breakdown[etype] = error_breakdown.get(etype, 0) + 1

    retrieval_ops = [
        r for r in records if r.get("tool_name") == "retrieval" and "tool_success" in r
    ]
    retrieval_success_count = sum(1 for r in retrieval_ops if r.get("tool_success") is True)
    retrieval_success_rate = (
        round((retrieval_success_count / len(retrieval_ops)) * 100, 1)
        if retrieval_ops
        else 100.0
    )

    # Cost
    costs = [r["cost_usd"] for r in responses_sent if "cost_usd" in r]
    total_cost = round(sum(costs), 4)

    # Tokens
    tokens_in = sum(r.get("tokens_in", 0) for r in responses_sent)
    tokens_out = sum(r.get("tokens_out", 0) for r in responses_sent)

    # Quality
    qualities = [r["quality_score"] for r in responses_sent if "quality_score" in r]
    quality_avg = round(sum(qualities) / len(qualities), 2) if qualities else 0.0

    return {
        "time_range_minutes": 60,
        "refresh_seconds": 30,
        "panels": {
            "latency": {
                "id": "latency",
                "title": "Latency percentiles and TTFT",
                "unit": "ms",
                "p50": p50,
                "p95": p95,
                "p99": p99,
                "ttft_p95": ttft_p95,
                "threshold": "P95 <= 3000 ms",
                "status": "PASS" if p95 <= 3000 else "BREACHED",
            },
            "traffic": {
                "id": "traffic",
                "title": "Request traffic",
                "unit": "req/min",
                "total_requests": traffic_count,
                "rate_per_minute": traffic_rate_pm,
                "threshold": "Rate >= 1 req/min",
                "status": "PASS" if traffic_rate_pm >= 1 else "BREACHED",
            },
            "errors": {
                "id": "errors",
                "title": "Error rate and retrieval success",
                "unit": "%",
                "error_rate_pct": error_rate_pct,
                "error_breakdown": error_breakdown,
                "retrieval_success_rate_pct": retrieval_success_rate,
                "threshold": "Error <= 2% | Retrieval >= 90%",
                "status": "PASS" if error_rate_pct <= 2 and retrieval_success_rate >= 90 else "BREACHED",
            },
            "cost": {
                "id": "cost",
                "title": "Cost over time",
                "unit": "USD",
                "total_cost_usd": total_cost,
                "threshold": "Total <= 2.50 USD",
                "status": "PASS" if total_cost <= 2.5 else "BREACHED",
            },
            "tokens": {
                "id": "tokens",
                "title": "Input and output tokens",
                "unit": "tokens",
                "tokens_in": tokens_in,
                "tokens_out": tokens_out,
                "tokens_total": tokens_in + tokens_out,
                "threshold": "Per field <= 50,000",
                "status": "PASS" if max(tokens_in, tokens_out) <= 50000 else "BREACHED",
            },
            "quality": {
                "id": "quality",
                "title": "Quality proxy",
                "unit": "score (0-1)",
                "mean_score": quality_avg,
                "threshold": "Mean >= 0.75",
                "status": "PASS" if quality_avg >= 0.75 else "BREACHED",
            },
        },
    }
