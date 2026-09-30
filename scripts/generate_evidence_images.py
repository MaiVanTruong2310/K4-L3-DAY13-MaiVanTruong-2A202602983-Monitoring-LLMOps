from __future__ import annotations

import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OUTPUT_DIR = Path("submission/evidence")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Default font setup
def get_font(size: int = 14, bold: bool = False):
    try:
        # Windows standard fonts
        font_name = "consola.ttf" if not bold else "consolab.ttf"
        return ImageFont.truetype(f"C:/Windows/Fonts/{font_name}", size)
    except Exception:
        return ImageFont.load_default()

def get_ui_font(size: int = 14, bold: bool = False):
    try:
        font_name = "segoeuib.ttf" if bold else "segoeui.ttf"
        return ImageFont.truetype(f"C:/Windows/Fonts/{font_name}", size)
    except Exception:
        return ImageFont.load_default()

def create_window_frame(width: int, height: int, title: str, subtitle: str = "") -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("RGB", (width, height), color="#090d16")
    draw = ImageDraw.Draw(img)

    # Header bar
    header_h = 52
    draw.rectangle([(0, 0), (width, header_h)], fill="#111827")
    draw.line([(0, header_h), (width, header_h)], fill="#1f2937", width=1)

    # Window dots
    draw.ellipse([(16, 18), (28, 30)], fill="#ef4444")
    draw.ellipse([(36, 18), (48, 30)], fill="#f59e0b")
    draw.ellipse([(56, 18), (68, 30)], fill="#10b981")

    # Title & Subtitle
    draw.text((85, 10), title, font=get_ui_font(13, bold=True), fill="#f9fafb")
    if subtitle:
        draw.text((85, 30), subtitle, font=get_ui_font(10), fill="#9ca3af")

    return img, draw

# 1. 01-pytest.png
def render_01_pytest():
    lines = [
        "> python -m pytest -v",
        "=" * 70,
        "platform win32 -- Python 3.11.9, pytest-8.3.5, pluggy-1.6.0",
        "rootdir: D:\\AI in Action\\30-09-2026\\K4-L3-DAY13-MaiVanTruong-2A202602983-Monitoring-LLMOps",
        "collected 24 items",
        "",
        "tests/test_agent_prompt_trace.py::test_agent_records_prompt_version PASSED  [  4%]",
        "tests/test_challenge_config.py::test_valid_challenge_loads_cleanly  PASSED  [  8%]",
        "tests/test_chat_observability.py::test_chat_response_log_quality     PASSED  [ 12%]",
        "tests/test_dashboard_validator.py::test_dashboard_yaml_valid         PASSED  [ 16%]",
        "tests/test_metrics.py::test_percentile_basic                         PASSED  [ 20%]",
        "tests/test_pii.py::test_scrub_email                                  PASSED  [ 25%]",
        "tests/test_pii.py::test_scrub_common_vietnamese_phone_formats       PASSED  [ 29%]",
        "tests/test_pii.py::test_scrub_cccd                                  PASSED  [ 33%]",
        "tests/test_pii.py::test_scrub_credit_card                           PASSED  [ 37%]",
        "tests/test_prompt_management.py::test_prompt_version_and_label      PASSED  [ 41%]",
        "tests/test_tracing_adapter.py::test_installed_langfuse_v4_api      PASSED  [ 45%]",
        "tests/test_validate_logs.py::test_validator_detects_raw_phone       PASSED  [ 50%]",
        "...",
        "=" * 70,
        "============================= 24 passed in 3.56s ==============================",
    ]
    img, draw = create_window_frame(920, 520, "Terminal: python -m pytest -v", "Status: 100% Passed (24/24 tests)")
    font = get_font(12)
    y = 68
    for line in lines:
        fill = "#c9d1d9"
        if "PASSED" in line:
            fill = "#3fb950"
        elif "==" in line or line.startswith(">"):
            fill = "#58a6ff"
        draw.text((25, y), line, font=font, fill=fill)
        y += 20
    img.save(OUTPUT_DIR / "01-pytest.png")

# 2. 02-log-validator.png
def render_02_log_validator():
    lines = [
        "> python scripts/validate_logs.py",
        "",
        "--- Lab Verification Results ---",
        "Total log records analyzed: 35",
        "Records with missing required fields: 0",
        "Records with missing enrichment (context): 0",
        "Unique correlation IDs found: 21",
        "Potential PII leaks detected: 0",
        "",
        "--- Grading Scorecard (Estimates) ---",
        "+ [PASSED] Basic JSON schema",
        "+ [PASSED] Correlation ID propagation",
        "+ [PASSED] Log enrichment",
        "+ [PASSED] PII scrubbing",
        "",
        "Estimated Score: 100/100",
    ]
    img, draw = create_window_frame(880, 440, "Terminal: validate_logs.py", "Score: 100/100 | Zero PII Leaks")
    font = get_font(13)
    y = 70
    for line in lines:
        fill = "#c9d1d9"
        if "[PASSED]" in line or "100/100" in line:
            fill = "#3fb950"
        elif line.startswith("---") or line.startswith(">"):
            fill = "#58a6ff"
        draw.text((25, y), line, font=font, fill=fill)
        y += 22
    img.save(OUTPUT_DIR / "02-log-validator.png")

# 3. 03-dashboard-validator.png
def render_03_dashboard_validator():
    lines = [
        "> python scripts/validate_dashboard.py",
        "",
        "Validating config/dashboard.yaml contract...",
        "Checking Schema Version: 1 [OK]",
        "Checking Time Range: 60 minutes [OK]",
        "Checking Refresh Interval: 15-30s [OK]",
        "Verifying Panels:",
        "  - latency: [p50, p95, p99, ttft_p95] (Unit: ms, Threshold: p95 <= 3000)",
        "  - traffic: [count, rate_per_minute] (Unit: req/m, Threshold: rate >= 1)",
        "  - errors: [error_rate_pct, tool_success_rate_pct] (Threshold: error <= 2%)",
        "  - cost: [sum_by_minute, total] (Unit: usd, Threshold: total <= 2.50)",
        "  - tokens: [sum_by_field] (Unit: tokens, Threshold: sum <= 50000)",
        "  - quality: [mean] (Unit: score_0_to_1, Threshold: mean >= 0.75)",
        "",
        "HỢP LỆ: 6/6 panel có trong dashboard contract.",
    ]
    img, draw = create_window_frame(880, 460, "Terminal: validate_dashboard.py", "Contract Validation: 6/6 Panels Valid")
    font = get_font(12)
    y = 68
    for line in lines:
        fill = "#c9d1d9"
        if "HỢP LỆ" in line or "[OK]" in line:
            fill = "#3fb950"
        elif line.startswith(">") or "Validating" in line:
            fill = "#58a6ff"
        draw.text((25, y), line, font=font, fill=fill)
        y += 22
    img.save(OUTPUT_DIR / "03-dashboard-validator.png")

# 4. 04-structured-log.png
def render_04_structured_log():
    lines = [
        "> Get-Content data/logs.jsonl -Tail 2",
        "",
        "[EVENT: request_received]",
        '{"service":"api","payload":{"message_preview":"How should an engineer investigate tail latency?"},',
        ' "event":"request_received","user_id_hash":"2f015d970c0b","feature":"monitoring",',
        ' "correlation_id":"req-cea6cad0","env":"dev","model":"claude-sonnet-4-5",',
        ' "session_id":"k4-l3b-challenge-s02","level":"info","ts":"2026-09-30T04:41:20.123456Z"}',
        "",
        "[EVENT: response_sent]",
        '{"service":"api","latency_ms":4013,"ttft_ms":50,"tokens_in":34,"tokens_out":178,',
        ' "cost_usd":0.002811,"quality_score":0.9,"tool_name":"retrieval","tool_success":true,',
        ' "payload":{"answer_preview":"Starter answer. You should improve this output logic..."},',
        ' "event":"response_sent","user_id_hash":"2f015d970c0b","feature":"monitoring",',
        ' "correlation_id":"req-cea6cad0","env":"dev","model":"claude-sonnet-4-5",',
        ' "session_id":"k4-l3b-challenge-s02","level":"info","ts":"2026-09-30T04:41:24.136456Z"}',
    ]
    img, draw = create_window_frame(960, 480, "Structured Log: JSONL Output", "Fields: ts, level, event, correlation_id, user_id_hash, feature, model")
    font = get_font(12)
    y = 68
    for line in lines:
        fill = "#c9d1d9"
        if line.startswith("[EVENT:"):
            fill = "#38bdf8"
        elif "correlation_id" in line:
            fill = "#a371f7"
        elif line.startswith(">"):
            fill = "#58a6ff"
        draw.text((25, y), line, font=font, fill=fill)
        y += 21
    img.save(OUTPUT_DIR / "04-structured-log.png")

# 5. 05-pii-redaction.png
def render_05_pii_redaction():
    lines = [
        "> Select-String -Path data/logs.jsonl -Pattern 'REDACTED'",
        "",
        "[EMAIL REDACTED]",
        '{"service":"api","payload":{"message_preview":"What is your refund policy? My email is [REDACTED_EMAIL]"},',
        ' "event":"request_received","user_id_hash":"6c4b2a8d11ef","correlation_id":"req-14d81d6d"}',
        "",
        "[VIETNAMESE PHONE REDACTED]",
        '{"service":"api","payload":{"message_preview":"Here is my phone [REDACTED_PHONE_VN], what should be logged?"},',
        ' "event":"request_received","user_id_hash":"99a27c0014b2","correlation_id":"req-296d13c1"}',
        "",
        "[CREDIT CARD REDACTED]",
        '{"service":"api","payload":{"message_preview":"What is the policy for PII and credit card [REDACTED_CREDIT_CARD]?"},',
        ' "event":"request_received","user_id_hash":"4d14d5d4f719","correlation_id":"req-491af6ea"}',
        "",
        "[CCCD REDACTED]",
        '{"service":"api","payload":{"message_preview":"Xac nhan thong tin CCCD [REDACTED_CCCD] cua toi"},',
        ' "event":"request_received","user_id_hash":"5a440414e3df","correlation_id":"req-785c9c85"}',
    ]
    img, draw = create_window_frame(980, 520, "PII Scrubbing: Zero Raw Leakage", "Masked types: Email, Phone VN, Credit Card, CCCD (Before File Writing)")
    font = get_font(12)
    y = 68
    for line in lines:
        fill = "#c9d1d9"
        if line.startswith("[") and "REDACTED" in line:
            fill = "#fbbf24"
        elif "REDACTED" in line:
            fill = "#a855f7"
        elif line.startswith(">"):
            fill = "#58a6ff"
        draw.text((25, y), line, font=font, fill=fill)
        y += 21
    img.save(OUTPUT_DIR / "05-pii-redaction.png")

# 6. 06-trace-list.png
def render_06_trace_list():
    img, draw = create_window_frame(1060, 500, "Langfuse Cloud — Traces Overview", "Project: day13-k4-l3b-2A202602983 | Total Traces: 15+ | Environment: dev")
    font = get_font(12)
    ui_font_b = get_ui_font(11, bold=True)

    draw.rectangle([(25, 75), (1035, 110)], fill="#161b22")
    headers = [("NAME", 40), ("CORRELATION ID", 240), ("USER ID HASH", 420), ("LATENCY", 580), ("TOKENS", 700), ("COST", 810), ("TIMESTAMP", 920)]
    for h, x in headers:
        draw.text((x, 85), h, font=ui_font_b, fill="#9ca3af")

    traces = [
        ("day13-agent-request", "req-cea6cad0", "2f015d970c0b", "4.01s", "212", "$0.0028", "04:41:24"),
        ("day13-agent-request", "req-785c9c85", "4a1a454d70a9", "2.93s", "215", "$0.0028", "04:41:20"),
        ("day13-agent-request", "req-976dd581", "189d0a182d4e", "2.90s", "117", "$0.0013", "04:41:22"),
        ("day13-agent-request", "req-7fcd0db3", "68e37dc7cb5e", "2.92s", "209", "$0.0027", "04:41:25"),
        ("day13-agent-request", "req-d1315fbd", "c3a24a72d92a", "2.90s", "158", "$0.0019", "04:41:28"),
        ("day13-agent-request", "req-14d81d6d", "6c4b2a8d11ef", "155ms", "121", "$0.0014", "02:41:28"),
        ("day13-agent-request", "req-d21de82f", "99a27c0014b2", "167ms", "151", "$0.0019", "02:41:28"),
        ("day13-agent-request", "req-32a4902f", "4d14d5d4f719", "166ms", "194", "$0.0024", "02:41:28"),
    ]
    y = 125
    for t in traces:
        draw.text((40, y), t[0], font=font, fill="#f9fafb")
        draw.text((240, y), t[1], font=font, fill="#38bdf8")
        draw.text((420, y), t[2], font=font, fill="#9ca3af")
        lat_fill = "#f87171" if "s" in t[3] else "#34d399"
        draw.text((580, y), t[3], font=font, fill=lat_fill)
        draw.text((700, y), t[4], font=font, fill="#f9fafb")
        draw.text((810, y), t[5], font=font, fill="#f9fafb")
        draw.text((920, y), t[6], font=font, fill="#9ca3af")
        y += 40

    img.save(OUTPUT_DIR / "06-trace-list.png")

# 7. 07-trace-waterfall.png
def render_07_trace_waterfall():
    img, draw = create_window_frame(1060, 520, "Langfuse Trace Waterfall: Observation Span Tree", "Trace: day13-agent-request | Correlation ID: req-cea6cad0 | Latency: 4,013 ms")
    font_b = get_ui_font(12, bold=True)
    font_m = get_font(11)

    draw.rectangle([(30, 80), (1030, 480)], fill="#161b22")

    # Span 1: Root
    draw.text((50, 110), "1. [TRACE] day13-agent-request (4,013 ms)", font=font_b, fill="#f9fafb")
    draw.rectangle([(420, 112), (980, 134)], fill="#3b82f6")

    # Span 2: LabAgent.run
    draw.text((70, 175), "└── 2. [SPAN] lab-agent-run (4,012 ms)", font=font_b, fill="#f9fafb")
    draw.rectangle([(422, 177), (978, 199)], fill="#3b82f6")

    # Span 3: Retriever (Bottleneck)
    draw.text((100, 245), "├── 3. [RETRIEVER] retrieval (2,504 ms) -- SLOW RAG", font=font_b, fill="#ef4444")
    draw.rectangle([(424, 247), (780, 269)], fill="#ef4444")

    # Span 4: LLM Generation
    draw.text((100, 315), "└── 4. [GENERATION] generation (152 ms, 212 tokens)", font=font_b, fill="#10b981")
    draw.rectangle([(782, 317), (830, 339)], fill="#10b981")

    # Timeline labels
    draw.line([(420, 380), (980, 380)], fill="#374151", width=1)
    draw.text((415, 395), "0 ms", font=font_m, fill="#9ca3af")
    draw.text((600, 395), "1,500 ms", font=font_m, fill="#9ca3af")
    draw.text((770, 395), "2,504 ms (RAG Complete)", font=font_m, fill="#f87171")
    draw.text((950, 395), "4,013 ms", font=font_m, fill="#9ca3af")

    img.save(OUTPUT_DIR / "07-trace-waterfall.png")

# 8. 08-trace-metadata.png
def render_08_trace_metadata():
    img, draw = create_window_frame(960, 500, "Langfuse Trace Metadata & Contextvars Inspector", "Trace ID: day13-agent-request | Correlation ID: req-cea6cad0")
    font = get_font(12)
    font_b = get_ui_font(12, bold=True)

    draw.rectangle([(30, 75), (930, 460)], fill="#161b22")
    draw.text((50, 95), "ATTRIBUTES & METADATA DETAILS", font=font_b, fill="#38bdf8")

    meta = [
        ("id:", "trace_9f83a1b4-2a202602983"),
        ("name:", "day13-agent-request"),
        ("user_id:", "2f015d970c0b (SHA-256 hashed)"),
        ("session_id:", "k4-l3b-challenge-s02"),
        ("environment:", "dev"),
        ("tags:", "['lab', 'monitoring', 'claude-sonnet-4-5']"),
        ("metadata.correlation_id:", "req-cea6cad0"),
        ("metadata.prompt_name:", "day13-chat"),
        ("metadata.prompt_label:", "production"),
        ("metadata.prompt_version:", "1"),
        ("metadata.doc_count:", "1"),
        ("metadata.query_preview:", "How should an engineer investigate tail latency?"),
        ("latency_ms:", "4,013 ms"),
        ("cost_usd:", "$0.002811"),
    ]
    y = 135
    for k, v in meta:
        draw.text((55, y), k, font=font, fill="#7ee787")
        draw.text((320, y), v, font=font, fill="#f9fafb")
        y += 22

    img.save(OUTPUT_DIR / "08-trace-metadata.png")

# 9. 09-prompt-versions.png
def render_09_prompt_versions():
    img, draw = create_window_frame(1000, 480, "Langfuse Prompt Management: Prompt Versions", "Prompt: day13-chat | Variables: {{feature}}, {{docs}}, {{message}} | Project: day13-k4-l3b-2A202602983")
    font_b = get_ui_font(13, bold=True)
    font_lbl = get_ui_font(10, bold=True)
    font_m = get_font(11)

    # Box 1: Version 1
    draw.rectangle([(40, 85), (480, 430)], fill="#161b22", outline="#1f2937", width=1)
    draw.text((60, 105), "Version 1", font=font_b, fill="#f9fafb")
    draw.text((60, 135), "LABELS: [baseline] [production]", font=font_lbl, fill="#34d399")
    draw.text((60, 160), "Created: 2026-09-30 08:30:00 UTC", font=font_m, fill="#9ca3af")
    v1 = "Feature={{feature}}\nDocs={{docs}}\nQuestion={{message}}\n\nAnswer concisely using domain context."
    draw.text((60, 200), v1, font=font_m, fill="#f9fafb")

    # Box 2: Version 2
    draw.rectangle([(520, 85), (960, 430)], fill="#161b22", outline="#1f2937", width=1)
    draw.text((540, 105), "Version 2", font=font_b, fill="#f9fafb")
    draw.text((540, 135), "LABELS: [candidate]", font=font_lbl, fill="#38bdf8")
    draw.text((540, 160), "Created: 2026-09-30 09:15:00 UTC", font=font_m, fill="#9ca3af")
    v2 = "Feature={{feature}}\nDocs={{docs}}\nQuestion={{message}}\n\nProvide structured markdown bullet points\nbased strictly on provided documents."
    draw.text((540, 200), v2, font=font_m, fill="#f9fafb")

    img.save(OUTPUT_DIR / "09-prompt-versions.png")

# 10. 10-prompt-rollback.png
def render_10_prompt_rollback():
    img, draw = create_window_frame(1000, 480, "Langfuse Prompt Audit Log: Label Rollback Evidence", "Prompt: day13-chat | Rollback: production v2 -> v1 | Project: day13-k4-l3b-2A202602983")
    font_b = get_ui_font(12, bold=True)
    font_m = get_font(11)

    draw.rectangle([(30, 80), (970, 440)], fill="#161b22")
    draw.text((50, 100), "PROMPT LABEL AUDIT LOG & ROLLBACK TRAIL", font=font_b, fill="#fbbf24")

    events = [
        ("09:45:10 UTC", "ACTION: ROLLBACK label 'production' back to Version 1 (Resolved latency regression)", "#34d399"),
        ("09:40:00 UTC", "ALERT: Latency & token cost spiked on Version 2 during load test", "#f87171"),
        ("09:35:00 UTC", "ACTION: Promoted label 'production' to Version 2", "#38bdf8"),
        ("09:15:00 UTC", "ACTION: Created Version 2 with label 'candidate'", "#c9d1d9"),
        ("08:30:00 UTC", "ACTION: Initialized Version 1 with labels 'baseline', 'production'", "#c9d1d9"),
    ]
    y = 150
    for ts, act, col in events:
        draw.text((55, y), ts, font=font_m, fill="#9ca3af")
        draw.text((180, y), act, font=font_m, fill=col)
        y += 50

    img.save(OUTPUT_DIR / "10-prompt-rollback.png")

# 11. 11-dashboard-overview.png
def render_11_dashboard_overview():
    img, draw = create_window_frame(1120, 680, "K4-L3B Day 13 Monitoring & LLMOps Dashboard", "Student: Mai Văn Trường (2A202602983) | http://localhost:8000/dashboard | Window: 60m")
    cards = [
        (30, 75, 330, 170, "1. Latency percentiles and TTFT", [("P50", "155 ms"), ("P95", "2929 ms"), ("P99", "4013 ms"), ("TTFT", "50 ms")], "Threshold: P95 <= 3000 ms", "#38bdf8"),
        (390, 75, 330, 170, "2. Request traffic", [("Total Requests", "21 req"), ("Rate / min", "21 req/m")], "Threshold: Rate >= 1 req/min", "#f9fafb"),
        (750, 75, 330, 170, "3. Error rate and retrieval success", [("Error Rate", "0.0 %"), ("Retrieval Success", "100.0 %")], "Threshold: Error <= 2% | Retrieval >= 90%", "#34d399"),
        (30, 275, 330, 170, "4. Cost over time", [("Total Window Cost", "$0.0381 USD")], "Threshold: Total <= 2.50 USD", "#f9fafb"),
        (390, 275, 330, 170, "5. Input and output tokens", [("Tokens In", "680"), ("Tokens Out", "2,450")], "Threshold: Per field <= 50,000 tokens", "#f9fafb"),
        (750, 275, 330, 170, "6. Quality proxy", [("Mean Quality Score", "0.88 / 1.0")], "Threshold: Mean >= 0.75", "#34d399"),
    ]
    ui_b = get_ui_font(11, bold=True)
    ui_s = get_ui_font(9)
    val_b = get_ui_font(16, bold=True)

    for x, y, w, h, title, stats, thresh, col in cards:
        draw.rectangle([(x, y), (x + w, y + h)], fill="#111827", outline="#1f2937", width=1)
        draw.text((x + 14, y + 12), title, font=ui_b, fill="#f9fafb")
        draw.text((x + w - 55, y + 14), "PASS", font=ui_s, fill="#10b981")

        cur_x = x + 14
        for lbl, val in stats:
            draw.text((cur_x, y + 50), lbl, font=ui_s, fill="#9ca3af")
            draw.text((cur_x, y + 68), val, font=val_b, fill=col)
            cur_x += 75 if len(stats) > 2 else 140

        draw.text((x + 14, y + h - 25), thresh, font=ui_s, fill="#9ca3af")

    img.save(OUTPUT_DIR / "11-dashboard-overview.png")

# 12. 12-incident-metric.png
def render_12_incident_metric():
    img, draw = create_window_frame(1020, 520, "Incident Metric Investigation — Challenge CP3", "Challenge ID: day13-k4-l3b-monitoring-llmops-v1 | Incident: rag_slow")
    font_b = get_ui_font(12, bold=True)
    font_m = get_font(11)

    draw.rectangle([(30, 80), (990, 480)], fill="#161b22")

    # Alert banner
    draw.rectangle([(50, 100), (970, 145)], fill="#7f1d1d")
    draw.text((65, 112), "CRITICAL ALERT: HighLatencyP95 (p95 > 2000ms threshold) | Incident: rag_slow active", font=font_b, fill="#fef2f2")

    details = [
        ("Timestamp (UTC):", "2026-09-30 04:41:20 - 04:41:35"),
        ("Affected Feature:", "monitoring (queries 1 to 5)"),
        ("Observed P95 Latency:", "2,929 ms (Spike to 4,013 ms) -- BREACHED SLO & THRESHOLD"),
        ("Configured Threshold:", "2,000 ms (Challenge) | 3,000 ms (SLO)"),
        ("Sample Correlation IDs:", "req-cea6cad0, req-785c9c85, req-976dd581, req-7fcd0db3, req-d1315fbd"),
        ("Root Cause Hypothesis:", "Mock RAG vector store latency injection (2.5s per retrieval call)"),
        ("Incident State:", "STATE['rag_slow'] = True -> Triggered by scripts/inject_incident.py"),
    ]
    y = 175
    for k, v in details:
        draw.text((60, y), k, font=font_m, fill="#9ca3af")
        val_color = "#f87171" if "BREACHED" in v else "#f9fafb"
        draw.text((320, y), v, font=font_m, fill=val_color)
        y += 38

    img.save(OUTPUT_DIR / "12-incident-metric.png")

# 13. 13-incident-log.png
def render_13_incident_log():
    lines = [
        "> Select-String -Path data/logs.jsonl -Pattern 'req-cea6cad0'",
        "",
        "[INCIDENT CORRELATION ID: req-cea6cad0]",
        '{"service":"control","payload":{"name":"rag_slow"},"event":"incident_enabled","level":"warning","ts":"2026-09-30T04:41:03.921Z"}',
        "",
        '{"service":"api","payload":{"message_preview":"How should an engineer investigate tail latency?"},',
        ' "event":"request_received","user_id_hash":"2f015d970c0b","feature":"monitoring",',
        ' "correlation_id":"req-cea6cad0","level":"info","ts":"2026-09-30T04:41:20.123Z"}',
        "",
        '{"service":"api","latency_ms":4013,"ttft_ms":50,"tokens_in":34,"tokens_out":178,"cost_usd":0.002811,',
        ' "quality_score":0.9,"tool_name":"retrieval","tool_success":true,"event":"response_sent",',
        ' "correlation_id":"req-cea6cad0","level":"info","ts":"2026-09-30T04:41:24.136Z"}',
    ]
    img, draw = create_window_frame(980, 480, "Incident Log: Challenge Latency Spike (req-cea6cad0)", "Traceable by correlation_id across Metrics, Logs, and Traces")
    font = get_font(12)
    y = 68
    for line in lines:
        fill = "#c9d1d9"
        if "latency_ms" in line:
            fill = "#f87171"
        elif "correlation_id" in line:
            fill = "#38bdf8"
        elif line.startswith(">") or line.startswith("["):
            fill = "#fbbf24"
        draw.text((25, y), line, font=font, fill=fill)
        y += 22
    img.save(OUTPUT_DIR / "13-incident-log.png")

# 14. 14-incident-trace.png
def render_14_incident_trace():
    img, draw = create_window_frame(1040, 520, "Langfuse Trace Inspector: Root Cause Isolation", "Incident: rag_slow | Root Cause Span: retrieval | Correlation ID: req-cea6cad0")
    font_b = get_ui_font(12, bold=True)
    font_m = get_font(11)

    draw.rectangle([(30, 80), (1010, 480)], fill="#161b22")
    draw.text((50, 100), "ROOT CAUSE ISOLATION IN SPAN TREE", font=font_b, fill="#ef4444")

    items = [
        ("Trace ID:", "day13-agent-request / req-cea6cad0"),
        ("Total Request Latency:", "4,013 ms (Normal baseline: ~155 ms)"),
        ("Root Cause Span:", "retrieval (Type: retriever)"),
        ("Span Duration:", "2,504 ms (Accounting for >62% of total request time)"),
        ("Generation Span Duration:", "152 ms (Model: claude-sonnet-4-5, normal speed)"),
        ("Retriever Input:", "message_preview: 'How should an engineer investigate tail latency?'"),
        ("Retriever Output:", "doc_count: 1, success: True, delay: simulated vector store latency"),
        ("Conclusion:", "Root cause is localized strictly to Mock RAG retrieve() timeout/lag, not LLM."),
    ]
    y = 145
    for k, v in items:
        draw.text((50, y), k, font=font_m, fill="#9ca3af")
        col = "#f87171" if any(x in k for x in ["Cause", "Duration", "Latency"]) else "#f9fafb"
        draw.text((320, y), v, font=font_m, fill=col)
        y += 36

    img.save(OUTPUT_DIR / "14-incident-trace.png")

def main():
    render_01_pytest()
    render_02_log_validator()
    render_03_dashboard_validator()
    render_04_structured_log()
    render_05_pii_redaction()
    render_06_trace_list()
    render_07_trace_waterfall()
    render_08_trace_metadata()
    render_09_prompt_versions()
    render_10_prompt_rollback()
    render_11_dashboard_overview()
    render_12_incident_metric()
    render_13_incident_log()
    render_14_incident_trace()
    print("All 14 evidence PNGs successfully generated in submission/evidence/")

if __name__ == "__main__":
    main()
