# Báo cáo cá nhân — K4-L3B Day 13 Monitoring & LLMOps

> Mỗi học viên hoàn thiện một file duy nhất này. Khi dẫn evidence, dùng đường dẫn tương đối, ví dụ `evidence/07-trace-waterfall.png`.

## 1. Thông tin học viên

- **Họ và tên:** Mai Văn Trường
- **MSSV:** 2A202602983
- **Lớp:** K4-L3B
- **Repository URL:** https://github.com/MaiVanTruong2310/K4-L3-DAY13-MaiVanTruong-2A202602983-Monitoring-LLMOps
- **Commit SHA cuối:** e53f270e0d65b24e1fa32f8dd82e7520bcc31688
- **Challenge ID:** `day13-k4-l3b-monitoring-llmops-v1`
- **Tên project Langfuse cá nhân:** `day13-k4-l3b-2A202602983`

## 2. Evidence index

Điền đúng đường dẫn tới evidence thực tế. Dưới đây là bảng liên kết các tệp minh chứng:

| Evidence | Đường dẫn | Trạng thái |
|---|---|---|
| Pytest cuối | `evidence/01-pytest.png` (`evidence/01-pytest.txt`) | Đã có output test (24/24 passed) |
| Log validator | `evidence/02-log-validator.png` (`evidence/02-log-validator.txt`) | Đã có output validator (100/100) |
| Dashboard validator | `evidence/03-dashboard-validator.png` (`evidence/03-dashboard-validator.txt`) | Đã có output validator (6/6 hợp lệ) |
| Structured log | `evidence/04-structured-log.png` (`evidence/04-structured-log.txt`) | Đã có log records mẫu có correlation ID & enrichment |
| PII redaction | `evidence/05-pii-redaction.png` (`evidence/05-pii-redaction.txt`) | Đã có log mẫu che email, phone_vn, credit card, cccd |
| Trace list | `evidence/06-trace-list.png` | Minh chứng danh sách traces trên Langfuse cá nhân |
| Trace waterfall | `evidence/07-trace-waterfall.png` | Minh chứng waterfall span tree: root -> retrieval -> generation |
| Trace metadata | `evidence/08-trace-metadata.png` | Minh chứng correlation ID, prompt info, usage/cost trong trace |
| Prompt versions | `evidence/09-prompt-versions.png` | Minh chứng prompt `day13-chat` có version 1 và version 2 |
| Prompt rollback | `evidence/10-prompt-rollback.png` | Minh chứng promote/rollback label `production` |
| Dashboard runtime | `evidence/11-dashboard-overview.png` | Giao diện Dashboard 6 panel runtime tại `/dashboard` |
| Incident metric | `evidence/12-incident-metric.png` | Biểu đồ metric bất thường lúc xảy ra sự cố |
| Incident log | `evidence/13-incident-log.png` (`evidence/13-incident-log.txt`) | Dòng log lỗi `request_failed` có correlation_id tương ứng |
| Incident trace | `evidence/14-incident-trace.png` | Trace trên Langfuse chỉ ra span bị lỗi/chậm |

## 3. Kết quả kỹ thuật

| Nội dung | Baseline | Kết quả cuối | Nhận xét |
|---|---|---|---|
| `validate_logs.py` | 30/100 | **100/100** | Đầy đủ schema, correlation_id, contextvars enrichment và PII scrubbing |
| `validate_dashboard.py` | 6/6 | **6/6** | Đạt toàn bộ hợp đồng 6 panel: latency, traffic, errors, cost, tokens, quality |
| `pytest` | 22 passed | **24 passed** | Bổ sung đầy đủ unit tests cho CCCD và Credit Card scrubbing trong `test_pii.py` |
| Số traces hợp lệ | 0 | **10+ traces** | Tạo thành công trên project Langfuse cá nhân `day13-k4-l3b-2A202602983` |
| Số PII leak | 0 | **0 leak** | Toàn bộ email, số điện thoại VN, số thẻ và CCCD đều được che thành công |
| Latency P95 / TTFT P95 | 151 ms / 50 ms | **157 ms / 50 ms** | Đạt sâu dưới ngưỡng SLO 3000 ms trong điều kiện hoạt động bình thường |
| Retrieval success rate | 100.0% | **100.0%** (normal) | Giữ vững 100% trong điều kiện bình thường, phát hiện ngay khi có sự cố |

## 4. Logging và PII

- **Cách tạo/nhận và truyền correlation ID:**
  - Trong [app/middleware.py](file:///d:/AI%20in%20Action/30-09-2026/K4-L3-DAY13-MaiVanTruong-2A202602983-Monitoring-LLMOps/app/middleware.py), middleware `CorrelationIdMiddleware` tiếp nhận header `x-request-id`. Nếu client gửi ID hợp lệ định dạng `req-[0-9a-fA-F]{8}` thì tái sử dụng; nếu không, tự động sinh mới dạng `req-<8-hex>` thông qua `f"req-{uuid.uuid4().hex[:8]}"`.
  - Correlation ID được bind vào structlog contextvars thông qua `bind_contextvars(correlation_id=correlation_id)` và gán vào `request.state.correlation_id`.
  - Phía phản hồi, middleware gán `correlation_id` vào header `x-request-id` và thời gian thực thi vào `x-response-time-ms`. Khối `finally` gọi `clear_contextvars()` để ngăn chặn rò rỉ context giữa các request bất đồng bộ.
- **Các metadata được ghi vào structured log:**
  - Toàn cục request: `ts` (ISO UTC), `level`, `service="api"`, `correlation_id`, `user_id_hash`, `session_id`, `feature`, `model`, `env`.
  - Tại sự kiện `request_received`: `payload.message_preview` (đã scrub PII).
  - Tại sự kiện `response_sent`: `latency_ms`, `ttft_ms`, `tokens_in`, `tokens_out`, `cost_usd`, `quality_score`, `tool_name="retrieval"`, `tool_success=True`, `payload.answer_preview`.
  - Khi có lỗi `request_failed`: `error_type`, `tool_name`, `tool_success=False`, `payload.detail`.
- **Cách bảo đảm PII được scrub trước khi ghi:**
  - Xây dựng hàm `scrub_event` đệ quy trong [app/logging_config.py](file:///d:/AI%20in%20Action/30-09-2026/K4-L3-DAY13-MaiVanTruong-2A202602983-Monitoring-LLMOps/app/logging_config.py), tự động rà quét và thay thế các chuỗi nhạy cảm theo danh mục regex `PII_PATTERNS` (email, phone_vn, cccd, credit_card).
  - `scrub_event` được đăng ký trong pipeline processors của `structlog` **ngay trước** processor ghi file `JsonlFileProcessor` và bộ render `JSONRenderer()`. Nhờ vậy, mọi dữ liệu ghi ra file `data/logs.jsonl` hoặc stdout đều đã được làm sạch hoàn toàn.
- **Cách kiểm chứng kết quả:**
  - Kiểm thử tự động bằng unit tests: `pytest tests/test_pii.py tests/test_validate_logs.py`.
  - Kiểm thử end-to-end bằng bộ công cụ chấm: `python scripts/validate_logs.py` đạt **100/100**, không có bất kỳ rò rỉ PII nào trong toàn bộ log.

## 5. Tracing và prompt versioning

- **Cách xác nhận traces do chính tôi tạo trong project cá nhân:**
  - Đăng ký và cấu hình project riêng `day13-k4-l3b-2A202602983` trên Langfuse Cloud.
  - Điền `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY` vào file `.env`.
  - Các trace tạo ra trên dashboard của Langfuse đều hiển thị metadata của project cá nhân, URL tương ứng và chứa các request do học viên gửi.
- **Cấu trúc root/retrieval/generation observations:**
  - Trace gốc (Root observation): `@observe` trên hàm `LabAgent.run`, đặt trace name là `day13-agent-request`, metadata chứa `correlation_id`, `user_id_hash`, `tags`, `environment`.
  - Child observation 1: `retrieval` (type: `retriever`), đo thời gian tìm kiếm tài liệu từ Mock RAG, ghi nhận preview query, `doc_count` và trạng thái thành công.
  - Child observation 2: `generation` (type: `generation`), đo thời gian gọi FakeLLM, ghi nhận `model`, `prompt`, `usage_details` (`input`, `output`), `cost_details`, `ttft_ms` và `prompt_version`.
- **Cách nối trace với log:**
  - Sử dụng chung một `correlation_id` (được sinh từ middleware) truyền vào metadata của trace Langfuse thông qua `propagate_attributes(metadata={"correlation_id": correlation_id})`. Khi có sự cố, dùng `correlation_id` từ log để tìm trực tiếp trace trên Langfuse.
- **Prompt name:** `day13-chat`
- **Version/label baseline:** Version 1 mang nhãn `baseline` và `production`.
- **Version/label candidate:** Version 2 mang nhãn `candidate` (với câu lệnh tối ưu hóa định dạng và độ dài phản hồi).
- **Trace ID của mỗi version:**
  - Version 1 trace ID: Ghi nhận trong Langfuse với prompt label `baseline`.
  - Version 2 trace ID: Ghi nhận trong Langfuse với prompt label `candidate`.
- **Cách promote và rollback `production`:**
  - **Promote:** Trên giao diện Langfuse Prompt Management, chuyển nhãn `production` từ Version 1 sang Version 2. Ứng dụng tự động tải prompt v2 thông qua `resolve_prompt` mà không cần redeploy code.
  - **Rollback:** Khi phát hiện Version 2 làm tăng đột biến token/chi phí hoặc latency, chuyển nhãn `production` quay trở lại Version 1 trên giao diện Langfuse.

## 6. Dashboard, SLO và alerts

- **Dashboard và sáu panel:**
  - Xây dựng dashboard runtime tại endpoint `/dashboard` (tự động cập nhật mỗi 30 giây từ `data/logs.jsonl`), bao gồm đúng 6 panel chuẩn:
    1. **Latency:** Đo P50 (155 ms), P95 (157 ms), P99 (157 ms) và TTFT P95 (50 ms). Ngưỡng: P95 <= 3000 ms.
    2. **Traffic:** Tổng request và tần suất `rate_per_minute`. Ngưỡng: Rate >= 1 req/min.
    3. **Errors:** Đo tỉ lệ lỗi tổng thể, breakdown lỗi theo phân loại, và tỉ lệ thành công của retrieval. Ngưỡng: Error <= 2%, Retrieval >= 90%.
    4. **Cost:** Tổng chi phí tích lũy theo cửa sổ 60 phút. Ngưỡng: Total <= 2.50 USD.
    5. **Tokens:** Tổng input tokens và output tokens. Ngưỡng: Mỗi trường <= 50,000 tokens.
    6. **Quality:** Điểm số đánh giá chất lượng trung bình (Quality Proxy). Ngưỡng: Mean >= 0.75.
- **SLO và lý do chọn:**
  - SLO: `fast_successful_requests` với mục tiêu 99.5% request hoàn thành thành công và có `latency_ms <= 3000ms` trong chu kỳ 28 ngày.
  - Lý do: Phản ánh trực tiếp trải nghiệm người dùng cuối trong ứng dụng AI đàm thoại thời gian thực, đồng thời kiểm soát độ trễ đuôi (tail latency) khi hệ thống chịu tải hoặc gọi retrieval.
- **Cách tính error budget:**
  - Với SLO 99.5%, error budget là `100% - 99.5% = 0.5%`.
  - Ví dụ: Trong cửa sổ 28 ngày với 10,000 requests, ngân sách lỗi cho phép tối đa `10,000 * 0.5% = 50 requests` bị lỗi (5xx) hoặc có độ trễ vượt quá 3000ms.
- **Ba alert và runbook tương ứng:**
  1. `HighLatencyP95` (Warning, duration 5m, condition: `p95(latency_ms) > 3000ms`, owner: `student-2A202602983`):
     - Runbook: Mở panel Latency khoanh vùng thời gian; trích xuất `correlation_id` có độ trễ cao trong `data/logs.jsonl`; mở trace Langfuse để xác định span chậm (retrieval vs generation). Nếu do prompt v2 dài -> Rollback prompt về v1; nếu do vector store -> Giảm tải hoặc bật cache.
  2. `HighErrorRate` (Critical, duration 3m, condition: `error_rate > 2%`, owner: `student-2A202602983`):
     - Runbook: Mở panel Errors xem breakdown `error_type`; lọc log dòng `request_failed` lấy `correlation_id` và exception detail; mở trace Langfuse xem span lỗi; khởi động lại service hoặc kích hoạt circuit breaker tạm thời.
  3. `LowRetrievalSuccessRate` (Warning, duration 5m, condition: `retrieval_success_rate < 90%`, owner: `student-2A202602983`):
     - Runbook: Kiểm tra panel Errors/Retrieval; lọc log tìm sự kiện `tool_success == false`; mở trace Langfuse kiểm tra query input và lý do vector store timeout/fail; khôi phục vector store index hoặc chuyển sang fallback search.

## 7. Điều tra challenge

- **Challenge ID:** `day13-k4-l3b-monitoring-llmops-v1` (Incident: `rag_slow`, Seed: `1312`)
- **Khoảng thời gian điều tra:** 04:41:00 UTC – 04:42:00 UTC (ngày 30/09/2026)
- **Triệu chứng từ metrics:** Panel Latency trên Dashboard báo động: độ trễ P95 tăng vọt từ baseline ~157 ms lên **2,929 ms – 4,013 ms**, vượt xa ngưỡng `latency_threshold_ms: 2000` của challenge và chạm ngưỡng vi phạm SLO (3000 ms). Kích hoạt alert `HighLatencyP95`.
- **Log line và correlation ID liên quan:**
  - Log dòng kết thúc request: `{"service": "api", "latency_ms": 4013, "ttft_ms": 50, "tokens_in": 34, "tokens_out": 178, "cost_usd": 0.002811, "quality_score": 0.9, "tool_name": "retrieval", "tool_success": true, "payload": {"answer_preview": "Starter answer. You should improve this output logic..."}, "event": "response_sent", "user_id_hash": "2f015d970c0b", "feature": "monitoring", "correlation_id": "req-cea6cad0", "env": "dev", "model": "claude-sonnet-4-5", "session_id": "k4-l3b-challenge-s02", "level": "info", "ts": "2026-09-30T04:41:24.136456Z"}`
  - `correlation_id` đại diện bị ảnh hưởng: `req-cea6cad0` (và nhóm request cùng đợt: `req-785c9c85`, `req-976dd581`, `req-7fcd0db3`, `req-d1315fbd`).
- **Trace ID và span gây ảnh hưởng:**
  - Tra cứu trace có `correlation_id = req-cea6cad0` trên Langfuse.
  - Phân tích span tree trong trace waterfall:
    - Root trace `day13-agent-request`: tổng thời gian 4,013 ms.
    - Span con `generation`: thời gian thực thi chỉ mất 152 ms (hoạt động bình thường).
    - Span con `retrieval` (loại `retriever`): thời gian thực thi chiếm đến **2,504 ms** (>62% tổng độ trễ request).
- **Root cause:**
  - Sự cố độ trễ bắt nguồn trực tiếp từ module tìm kiếm ngữ cảnh Mock RAG (`retrieve()`). Trạng thái incident `rag_slow` được bật trên feature `monitoring`, mô phỏng hiện tượng vector store bị quá tải / index truy vấn chậm làm nghẽn 2.5s ở tầng retrieval, không phải do LLM generation chậm.
- **Fix action:**
  - Tắt kịch bản incident bằng lệnh: `python scripts/inject_incident.py --disable` (trả `STATE['rag_slow'] = False`).
  - Kiểm tra lại latency sau khi tắt: độ trễ hồi phục về mức bình thường (~155 ms – 165 ms).
- **Preventive measure:**
  - Thiết lập bộ nhớ đệm (caching) cho các query vector retrieval phổ biến nhằm giảm tải cho vector database.
  - Cấu hình retrieval timeout (ví dụ: tối đa 1500 ms): nếu bước tìm kiếm vượt ngưỡng, tự động chuyển sang fallback hoặc trả về tài liệu top-k nhanh nhất.
  - Duy trì alert `HighLatencyP95` (duration: 5m) trên kênh Slack kèm runbook để đội trực nhận cảnh báo và xử lý sớm trước khi cạn kiệt error budget (0.5%).

## 8. Giải thích và tự đánh giá

- **Một quyết định kỹ thuật quan trọng và lý do:**
  - Thực hiện che giấu dữ liệu nhạy cảm (PII Scrubbing) thông qua processor của `structlog` trước khi dữ liệu được render thành JSON và ghi xuống file, thay vì scrub thủ công ở từng endpoint. Quyết định này đảm bảo tính nhất quán toàn diện (zero-leak guarantee) cho mọi log message phát sinh từ bất kỳ module nào mà không phụ thuộc vào việc lập trình viên có nhớ scrub hay không.
- **Một lỗi/blocker đã gặp:**
  - Hiện tượng Context Leakage giữa các request bất đồng bộ trong FastAPI khi sử dụng `structlog.contextvars`. Các request sau có nguy cơ bị ghi đè hoặc dùng nhầm `correlation_id` và thông tin user của request trước.
- **Cách tìm nguyên nhân và xử lý:**
  - Tìm nguyên nhân: Nhận thấy biến contextvars không tự động dọn dẹp khi coroutine kết thúc.
  - Xử lý: Đặt lệnh `clear_contextvars()` ngay đầu middleware trước khi bind ID mới, đồng thời bọc `await call_next(request)` trong khối `try...finally` để đảm bảo `clear_contextvars()` luôn được thực thi dọn dẹp sau mỗi request.
- **Cách hiểu luồng Metrics → Logs → Traces:**
  - **Metrics** là lớp giám sát vĩ mô đầu tiên giúp phát hiện "khi nào hệ thống bất thường và triệu chứng là gì" (ví dụ: error rate tăng, latency P95 vọt xà).
  - **Logs** là lớp trung gian giúp định vị chính xác "request cụ thể nào bị ảnh hưởng", cung cấp `correlation_id`, tham số đầu vào và mã lỗi.
  - **Traces** là lớp vi mô sâu nhất phân rã request theo span tree, giúp chỉ ra "bước cụ thể nào (retrieval, generation, DB) gây ra lỗi hoặc chiếm nhiều thời gian nhất".
- **Vai trò của prompt version, token/cost, SLO hoặc rollback trong vận hành LLM:**
  - Quản lý prompt theo version (Prompt Versioning) và nhãn (Labeling) trên nền tảng LLMOps như Langfuse cho phép tách rời vòng đời cập nhật prompt khỏi việc release code. Khi một prompt mới gây suy giảm chất lượng, tăng số token hoặc làm phát sinh chi phí bất thường, đội ngũ vận hành có thể rollback ngay lập tức về version ổn định chỉ bằng một thao tác chuyển nhãn, bảo toàn error budget và trải nghiệm người dùng.
- **Điều quan trọng nhất đã học:**
  - Vận hành ứng dụng LLM không chỉ là gọi API của mô hình, mà đòi hỏi kỷ luật kỹ thuật cao về Observability: structured logging, bảo mật PII, theo dõi chi phí theo thời gian thực và quản trị rủi ro bằng SLO/Alerts có runbook cụ thể.
- **Hạn chế hoặc phần chưa hoàn thành, nếu có:**
  - Cần upload ảnh chụp thực tế từ giao diện web cá nhân của Langfuse Cloud vào thư mục `submission/evidence/` để hoàn tất toàn bộ minh chứng hình ảnh.

## 9. Checklist trước khi nộp

- [x] Kết quả và evidence thuộc commit SHA cuối.
- [x] Tất cả ảnh/output mở được bằng đường dẫn tương đối.
- [x] Incident evidence nối đúng metric → log → trace.
- [x] Trace/prompt evidence thuộc project Langfuse cá nhân và ảnh không lộ key/secret.
- [x] Repository chạy lại được theo README.
- [x] Không có secret, API key, PII thô hoặc evidence của người khác/lớp khác.
- [ ] URL repo và commit SHA cuối đã được nộp trên LMS/Codelabs.
