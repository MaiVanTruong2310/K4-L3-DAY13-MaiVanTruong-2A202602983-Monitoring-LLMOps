from __future__ import annotations

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from structlog.contextvars import bind_contextvars

from .agent import LabAgent
from .dashboard import compute_dashboard_metrics
from .incidents import disable, enable, status
from .logging_config import configure_logging, get_logger
from .metrics import record_error, snapshot
from .middleware import CorrelationIdMiddleware
from .pii import hash_user_id, scrub_text, summarize_text
from .schemas import ChatRequest, ChatResponse
from .tracing import tracing_enabled

configure_logging()
log = get_logger()
agent = LabAgent()


@asynccontextmanager
async def lifespan(_: FastAPI):
    log.info(
        "app_started",
        service=os.getenv("APP_NAME", "day13-monitoring-llmops-lab"),
        env=os.getenv("APP_ENV", "dev"),
        payload={"tracing_enabled": tracing_enabled()},
    )
    yield


app = FastAPI(title="Day 13 Monitoring & LLMOps Lab", lifespan=lifespan)
app.add_middleware(CorrelationIdMiddleware)


@app.get("/health")
async def health() -> dict:
    return {"ok": True, "tracing_enabled": tracing_enabled(), "incidents": status()}


@app.get("/metrics")
async def metrics() -> dict:
    return snapshot()


@app.get("/api/dashboard/stats")
async def dashboard_stats() -> dict:
    return compute_dashboard_metrics()


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page() -> str:
    data = compute_dashboard_metrics()
    p = data.get("panels", {})
    lat = p.get("latency", {})
    traf = p.get("traffic", {})
    err = p.get("errors", {})
    cost = p.get("cost", {})
    tok = p.get("tokens", {})
    qual = p.get("quality", {})

    def badge(status_val: str) -> str:
        color = "#10b981" if status_val == "PASS" else "#ef4444"
        return f'<span style="background: {color}22; color: {color}; padding: 3px 8px; border-radius: 9999px; font-size: 11px; font-weight: 600; border: 1px solid {color}44;">{status_val}</span>'

    breakdown = err.get("error_breakdown", {})
    breakdown_html = (
        ", ".join(f'<span class="breakdown-tag">{k}: {v}</span>' for k, v in breakdown.items())
        if breakdown
        else "None"
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="refresh" content="30">
    <title>K4-L3B Day 13 Monitoring &amp; LLMOps Dashboard</title>
    <style>
        :root {{
            --bg: #090d16;
            --card-bg: #111827;
            --card-border: #1f2937;
            --text-main: #f9fafb;
            --text-muted: #9ca3af;
            --accent: #3b82f6;
            --font: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            background: var(--bg);
            color: var(--text-main);
            font-family: var(--font);
            padding: 24px;
        }}
        header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 24px;
            padding-bottom: 16px;
            border-bottom: 1px solid var(--card-border);
        }}
        h1 {{ font-size: 22px; font-weight: 700; }}
        .header-meta {{ display: flex; gap: 16px; font-size: 13px; color: var(--text-muted); }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
            gap: 20px;
        }}
        .card {{
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 12px;
            padding: 20px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.3);
        }}
        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 14px;
        }}
        .card-title {{ font-size: 15px; font-weight: 600; color: #e5e7eb; }}
        .metrics-row {{
            display: flex;
            gap: 16px;
            margin-bottom: 16px;
            flex-wrap: wrap;
        }}
        .metric-item {{ flex: 1; min-width: 65px; }}
        .metric-label {{ font-size: 12px; color: var(--text-muted); margin-bottom: 4px; }}
        .metric-val {{ font-size: 24px; font-weight: 700; color: #fff; }}
        .metric-unit {{ font-size: 12px; color: var(--text-muted); font-weight: normal; margin-left: 2px; }}
        .threshold-box {{
            font-size: 12px;
            padding: 8px 12px;
            background: rgba(255,255,255,0.03);
            border-radius: 6px;
            border-left: 3px solid var(--accent);
            color: var(--text-muted);
            margin-top: auto;
        }}
        .breakdown-tag {{
            font-size: 11px;
            background: #1f2937;
            padding: 2px 6px;
            border-radius: 4px;
            margin-right: 4px;
        }}
    </style>
</head>
<body>
    <header>
        <div>
            <h1>K4-L3B Day 13 Monitoring &amp; LLMOps Dashboard</h1>
            <p style="font-size: 13px; color: var(--text-muted); margin-top: 4px;">Student: Mai Văn Trường (MSSV: 2A202602983) | Source: <code>data/logs.jsonl</code></p>
        </div>
        <div class="header-meta">
            <span>⏱️ Window: <strong>60 min</strong></span>
            <span>🔄 Refresh: <strong>30s</strong></span>
            <span>🟢 Status: <strong>LIVE</strong></span>
        </div>
    </header>

    <div class="grid">
        <!-- 1. Latency -->
        <div class="card">
            <div class="card-header">
                <span class="card-title">1. Latency percentiles and TTFT</span>
                {badge(lat.get("status", "PASS"))}
            </div>
            <div class="metrics-row">
                <div class="metric-item">
                    <div class="metric-label">P50</div>
                    <div class="metric-val">{lat.get("p50", 0):.0f}<span class="metric-unit">ms</span></div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">P95</div>
                    <div class="metric-val">{lat.get("p95", 0):.0f}<span class="metric-unit">ms</span></div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">P99</div>
                    <div class="metric-val">{lat.get("p99", 0):.0f}<span class="metric-unit">ms</span></div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">TTFT P95</div>
                    <div class="metric-val">{lat.get("ttft_p95", 0):.0f}<span class="metric-unit">ms</span></div>
                </div>
            </div>
            <div class="threshold-box">Threshold / SLO: <strong>P95 &le; 3000 ms</strong></div>
        </div>

        <!-- 2. Traffic -->
        <div class="card">
            <div class="card-header">
                <span class="card-title">2. Request traffic</span>
                {badge(traf.get("status", "PASS"))}
            </div>
            <div class="metrics-row">
                <div class="metric-item">
                    <div class="metric-label">Total Requests</div>
                    <div class="metric-val">{traf.get("total_requests", 0)}</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">Rate / min</div>
                    <div class="metric-val">{traf.get("rate_per_minute", 0)}<span class="metric-unit">req/m</span></div>
                </div>
            </div>
            <div class="threshold-box">Threshold: <strong>Rate &ge; 1 req/min</strong></div>
        </div>

        <!-- 3. Errors -->
        <div class="card">
            <div class="card-header">
                <span class="card-title">3. Error rate and retrieval success</span>
                {badge(err.get("status", "PASS"))}
            </div>
            <div class="metrics-row">
                <div class="metric-item">
                    <div class="metric-label">Error Rate</div>
                    <div class="metric-val">{err.get("error_rate_pct", 0)}<span class="metric-unit">%</span></div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">Retrieval Success</div>
                    <div class="metric-val">{err.get("retrieval_success_rate_pct", 100)}<span class="metric-unit">%</span></div>
                </div>
            </div>
            <div style="font-size: 12px; color: var(--text-muted); margin-bottom: 8px;">
                Errors breakdown: {breakdown_html}
            </div>
            <div class="threshold-box">Threshold: <strong>Error &le; 2% | Retrieval &ge; 90%</strong></div>
        </div>

        <!-- 4. Cost -->
        <div class="card">
            <div class="card-header">
                <span class="card-title">4. Cost over time</span>
                {badge(cost.get("status", "PASS"))}
            </div>
            <div class="metrics-row">
                <div class="metric-item">
                    <div class="metric-label">Total Window Cost</div>
                    <div class="metric-val">${cost.get("total_cost_usd", 0):.4f}</div>
                </div>
            </div>
            <div class="threshold-box">Threshold: <strong>Total &le; 2.50 USD</strong></div>
        </div>

        <!-- 5. Tokens -->
        <div class="card">
            <div class="card-header">
                <span class="card-title">5. Input and output tokens</span>
                {badge(tok.get("status", "PASS"))}
            </div>
            <div class="metrics-row">
                <div class="metric-item">
                    <div class="metric-label">Tokens In</div>
                    <div class="metric-val">{tok.get("tokens_in", 0):,}</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">Tokens Out</div>
                    <div class="metric-val">{tok.get("tokens_out", 0):,}</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">Total</div>
                    <div class="metric-val">{tok.get("tokens_total", 0):,}</div>
                </div>
            </div>
            <div class="threshold-box">Threshold: <strong>Per field &le; 50,000 tokens</strong></div>
        </div>

        <!-- 6. Quality -->
        <div class="card">
            <div class="card-header">
                <span class="card-title">6. Quality proxy</span>
                {badge(qual.get("status", "PASS"))}
            </div>
            <div class="metrics-row">
                <div class="metric-item">
                    <div class="metric-label">Mean Quality Score</div>
                    <div class="metric-val">{qual.get("mean_score", 0):.2f}<span class="metric-unit">/ 1.0</span></div>
                </div>
            </div>
            <div class="threshold-box">Threshold: <strong>Mean &ge; 0.75</strong></div>
        </div>
    </div>
</body>
</html>
"""


@app.post("/chat", response_model=ChatResponse)
async def chat(request: Request, body: ChatRequest) -> ChatResponse:
    bind_contextvars(
        user_id_hash=hash_user_id(body.user_id),
        session_id=scrub_text(body.session_id),
        feature=scrub_text(body.feature),
        model=agent.model,
        env=os.getenv("APP_ENV", "dev"),
    )
    log.info(
        "request_received",
        service="api",
        payload={"message_preview": summarize_text(body.message)},
    )
    try:
        result = agent.run(
            user_id=body.user_id,
            feature=body.feature,
            session_id=body.session_id,
            message=body.message,
            correlation_id=request.state.correlation_id,
        )
        log.info(
            "response_sent",
            service="api",
            latency_ms=result.latency_ms,
            ttft_ms=result.ttft_ms,
            tokens_in=result.tokens_in,
            tokens_out=result.tokens_out,
            cost_usd=result.cost_usd,
            quality_score=result.quality_score,
            tool_name="retrieval",
            tool_success=True,
            payload={"answer_preview": summarize_text(result.answer)},
        )
        return ChatResponse(
            answer=result.answer,
            correlation_id=request.state.correlation_id,
            latency_ms=result.latency_ms,
            ttft_ms=result.ttft_ms,
            tokens_in=result.tokens_in,
            tokens_out=result.tokens_out,
            cost_usd=result.cost_usd,
            quality_score=result.quality_score,
        )
    except Exception as exc:  # pragma: no cover
        error_type = type(exc).__name__
        record_error(error_type)
        log.error(
            "request_failed",
            service="api",
            error_type=error_type,
            tool_name="retrieval" if isinstance(exc, RuntimeError) else None,
            tool_success=False if isinstance(exc, RuntimeError) else None,
            payload={"detail": str(exc), "message_preview": summarize_text(body.message)},
        )
        raise HTTPException(status_code=500, detail=error_type) from exc


@app.post("/incidents/{name}/enable")
async def enable_incident(name: str) -> JSONResponse:
    try:
        enable(name)
        log.warning("incident_enabled", service="control", payload={"name": name})
        return JSONResponse({"ok": True, "incidents": status()})
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/incidents/{name}/disable")
async def disable_incident(name: str) -> JSONResponse:
    try:
        disable(name)
        log.warning("incident_disabled", service="control", payload={"name": name})
        return JSONResponse({"ok": True, "incidents": status()})
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
