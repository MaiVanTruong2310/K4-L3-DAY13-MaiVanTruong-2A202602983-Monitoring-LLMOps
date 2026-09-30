# Template Alert và Runbook

Mỗi alert phải dựa trên triệu chứng người dùng hoặc SLO, không dựa trực tiếp vào tên implementation nội bộ.

## Alert mẫu để tham khảo

Ví dụ dưới đây minh họa mức độ cụ thể cần có. Học viên không cần copy nguyên, nhưng ba alert trong bài nộp nên rõ ràng tương tự: điều kiện là gì, kéo dài bao lâu, ảnh hưởng tới user ra sao và người trực cần kiểm tra gì trước.

- Tên: `HighLatencyP95`
- Severity: `warning`
- Duration: `5m`
- Kênh thông báo: Slack `#k4-l3b-alerts`
- SLI/SLO liên quan: latency P95 của `response_sent.latency_ms`
- Điều kiện và thời gian duy trì: `p95(latency_ms) > 3000ms` trong 5 phút
- Ảnh hưởng tới người dùng: người dùng phải chờ lâu hơn trước khi nhận câu trả lời
- Ba bước kiểm tra đầu tiên:
  1. Mở dashboard latency để xác nhận P95/P99 và khoảng thời gian tăng.
  2. Lọc `data/logs.jsonl` trong khoảng đó, lấy một `correlation_id` có `latency_ms` cao.
  3. Mở trace cùng `correlation_id` trên Langfuse, so sánh các span chính để xác định bước nào bất thường.
- Mitigation tạm thời: dựa trên evidence thực tế để rollback prompt, khôi phục cấu hình liên quan, tắt practice scenario hoặc giảm tải khi demo.
- Owner: `student-<MSSV>`

## Alert 1

- Tên: `HighLatencyP95`
- Severity: `warning`
- Duration: `5m`
- Kênh thông báo: Slack `#k4-l3b-alerts`
- SLI/SLO liên quan: `p95(latency_ms)` của `response_sent.latency_ms` (SLO <= 3000ms)
- Điều kiện và thời gian duy trì: `p95(latency_ms) > 3000ms` liên tục trong 5 phút
- Ảnh hưởng tới người dùng: Người dùng phải chờ lâu hơn trước khi nhận được phản hồi từ AI API, trải nghiệm giảm sút, nguy cơ timeout phía client.
- Ba bước kiểm tra đầu tiên:
  1. Mở dashboard panel Latency để xác nhận P50/P95/P99 và khoảng thời gian latency bắt đầu tăng vọt.
  2. Lọc `data/logs.jsonl` trong khung giờ đó để lấy một `correlation_id` của request có `latency_ms` cao bất thường.
  3. Mở trace có cùng `correlation_id` trên Langfuse, so sánh thời gian thực thi của span `retrieval` và `generation` để xác định nghẽn ở bước nào.
- Mitigation tạm thời: Nếu do prompt mới làm tăng token/generation time thì rollback prompt label `production` về version ổn định trước đó; nếu do retrieval chậm thì kiểm tra mock RAG / database và áp dụng caching/giới hạn tải.
- Owner: `student-2A202602983`

## Alert 2

- Tên: `HighErrorRate`
- Severity: `critical`
- Duration: `3m`
- Kênh thông báo: Slack `#k4-l3b-alerts`
- SLI/SLO liên quan: Tỉ lệ lỗi tổng thể `count(request_failed) / count(request_received)` (SLO error rate <= 2%)
- Điều kiện và thời gian duy trì: `error_rate > 2%` liên tục trong 3 phút
- Ảnh hưởng tới người dùng: Nhiều request của người dùng bị gián đoạn, API trả về HTTP 5xx hoặc message lỗi, làm cạn kiệt nhanh error budget (0.5% trong 28 ngày).
- Ba bước kiểm tra đầu tiên:
  1. Mở dashboard panel Errors để xem error rate và breakdown theo `error_type` (downstream timeout, internal error, v.v.).
  2. Tra cứu `data/logs.jsonl` tìm các log record có `level == "error"` hoặc `event == "request_failed"` để trích xuất `correlation_id` và stack trace lỗi.
  3. Mở trace trên Langfuse theo `correlation_id` đó để xem chính xác span bị throw exception hoặc HTTP status code lỗi.
- Mitigation tạm thời: Khởi động lại service nếu do crash nội bộ; nếu do downstream dependency hoặc prompt injection làm sập service thì bật fallback response hoặc circuit breaker tạm thời.
- Owner: `student-2A202602983`

## Alert 3

- Tên: `LowRetrievalSuccessRate`
- Severity: `warning`
- Duration: `5m`
- Kênh thông báo: Slack `#k4-l3b-alerts`
- SLI/SLO liên quan: Guardrail `retrieval_success_rate` (tối thiểu 90%)
- Điều kiện và thời gian duy trì: `retrieval_success_rate < 90%` liên tục trong 5 phút
- Ảnh hưởng tới người dùng: Mô hình không nhận được tài liệu ngữ cảnh cần thiết (context), dẫn đến câu trả lời bị hallucination, thiếu chính xác hoặc điểm quality score sụt giảm.
- Ba bước kiểm tra đầu tiên:
  1. Mở dashboard panel Errors/Retrieval kiểm tra tỉ lệ `tool_success` của retriever và panel Quality xem `quality_score` có bị giảm đồng thời hay không.
  2. Lọc `data/logs.jsonl` tìm các dòng có `tool_name == "retrieval"` và `tool_success == false`, lấy `correlation_id`.
  3. Mở trace trên Langfuse để xem span `retrieval`: kiểm tra query input preview, metadata `doc_count` và lỗi trả về từ retriever.
- Mitigation tạm thời: Kiểm tra kho dữ liệu/vector index của RAG; nếu index bị lỗi hoặc quá tải thì chuyển sang chế độ fallback retrieval hoặc khôi phục snapshot vector store gần nhất.
- Owner: `student-2A202602983`
