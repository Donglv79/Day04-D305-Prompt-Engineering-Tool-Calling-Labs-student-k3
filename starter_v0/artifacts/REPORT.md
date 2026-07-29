# Day 04 Lab v2 Report — Research Agent

## Team

- Team: B2
- Members:
  - Lê Văn Đông - 2A202601851
  - Đào Đức Mạnh - 2A202601833
  - Nguyễn Viết Huy - 2A202601081
  - Đàm Lê Minh Quân - 2A202601451
  - Trần Văn Dũng - 2A202601859
- Provider/model: Gemini / gemini-3.5-flash

---

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

Research Agent hỗ trợ tìm kiếm tin tức công nghệ đa nguồn (Web, Twitter/X, bài báo khoa học arXiv), đọc và trích xuất tài liệu nội bộ, đồng thời hỗ trợ tổng hợp thông tin và gửi bản tin tự động lên kênh Telegram sau khi được xác nhận.

**Link dùng thử (truy cập được trong showdown):**

> URL: http://localhost:8501

## A2. Tool agent có

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | Hỏi lại người dùng khi thiếu thông tin hoặc xin xác nhận yes_no trước khi thực hiện hành động | không |
| lookup | Tìm kiếm thông tin tổng hợp trên Web qua API Tavily | không |
| fetch | Đọc và trích xuất nội dung bài viết từ một đường link URL qua Firecrawl | không |
| timeline | Lấy các bài đăng gần đây của một tài khoản Twitter qua RapidAPI | không |
| social_search | Tìm kiếm bài đăng trên mạng xã hội theo từ khóa qua RapidAPI | không |
| format | Trình bày các thông tin đã thu thập thành bản digest markdown chuẩn mực | không |
| dedupe_sources | Loại bỏ các nguồn trùng và làm sạch URL tracking trong danh sách nghiên cứu | **CÓ (Nhóm viết)** |
| source_quality_check | Kiểm tra chất lượng và độ tin cậy metadata của các research item | **CÓ (Nhóm viết)** |
| extract_citations | Trích xuất và định dạng danh sách trích dẫn nguồn (numbered, markdown, inline) | **CÓ (Nhóm viết)** |
| filter_sources | Lọc danh sách nguồn theo domain, từ khóa, HTTPS và độ dài summary | **CÓ (Nhóm viết)** |
| send | Gửi bản tin/tin nhắn tới kênh Telegram (yêu cầu xác nhận người dùng) | không |
| policy | Tra cứu quy định và chính sách sử dụng AI/trích dẫn của công ty | không |
| papers | Tìm kiếm bài báo khoa học công nghệ trên arXiv | không |
| paper_text | Tải PDF và trích xuất văn bản từ bài báo arXiv | không |

## A3. Câu hỏi mẫu để thử

1. "Tìm giúp mình 5 bài báo mới nhất trên arXiv về Generative AI và tóm tắt lại."
2. "Lấy 10 bài đăng mới nhất từ tài khoản Twitter @elonmusk."
3. "Chuẩn bị gửi bản tin 'Cập nhật AI hôm nay' lên Telegram." *(Agent sẽ hỏi xin xác nhận yes/no trước khi gửi)*

## A4. Kịch bản demo đã rehearse

| Scenario | Tool trace cần thấy | Câu chuyện cải thiện version | Fallback run/transcript |
|---|---|---|---|
| Tra cứu bài đăng Twitter @elonmusk | `timeline(screenname="elonmusk", limit=10)` | v0 trích xuất sai username ➔ v3 tự động map tên sang screenname chính xác | `runs/v3_B_base_openrouter_20260729T103709326371.json` |
| Yêu cầu gửi tin nhắn Telegram | `clarify(response_type="yes_no")` ➔ `send(confirmed=true)` | v0 tự ý gửi không xin phép ➔ v3 bắt buộc hỏi xác nhận trước khi gửi | `runs/v3_B_group_gemini_20260729T113430960537.json` |
| Tra cứu chính sách công ty | `policy(policy_area="source_citation")` | v0 nhầm với web search ➔ v3 định tuyến chính xác vào tài liệu nội bộ | `runs/v3_B_group_gemini_20260729T113430960537.json` |

---

# PHẦN B — Chi tiết / Bằng chứng

## B1. Version evidence

Dữ liệu được trích xuất trực tiếp từ `artifacts/version_log.csv` và các file `runs/*.json`:

| Version | Prompt/tool change | Hypothesis | Metric name | Before | After | Run File |
|---|---|---|---|---:|---:|---|
| v0 | baseline | Baseline trước khi tối ưu; system prompt gốc dặn agent đoán bừa | case_accuracy | - | 0.70 | `runs/v0_B_base_openrouter_20260729T100315014353.json` |
| v1 | `system_prompt.md` | Xóa câu "đoán bừa", dặn ép gọi clarify khi thiếu tin / xin phép trước khi send | case_accuracy | 0.70 | 0.85 | `runs/v1_B_base_openrouter_20260729T102905751717.json` |
| v2 | `system_prompt.md` | Nêu rõ quy tắc chọn response_type ('text' cho thông tin, 'yes_no' cho xác nhận) | case_accuracy | 0.85 | 0.90 | `runs/v2_B_base_openrouter_20260729T103249328295.json` |
| v3 | `tools.yaml` | Đưa confirmation boundary vào chính tool declaration của `send` | case_accuracy | 0.90 | 1.00 | `runs/v3_B_base_openrouter_20260729T103709326371.json` |

### So sánh chi tiết ưu & nhược điểm giữa các phiên bản

#### 1. Phiên bản v0 (Baseline)
* **Trạng thái:** Baseline ban đầu của hệ thống.
* **Độ chính xác:** 70%.
* **Ưu điểm:** Tốc độ phản hồi nhanh do không mất lượt gọi hỏi lại (`clarify`).
* **Nhược điểm:** Tự đoán thông tin bị thiếu và tự ý gửi tin nhắn lên Telegram mà không xin phép (vi phạm ranh giới hành động nhạy cảm).

#### 2. Phiên bản v1
* **Thay đổi:** Xóa hướng dẫn tiêu cực khỏi `system_prompt.md`. Thêm chỉ dẫn bắt buộc gọi tool `clarify` khi thiếu thông tin và hỏi `yes_no` trước khi `send`.
* **Độ chính xác:** Tăng từ 70% lên 85%.
* **Ưu điểm:** Hạn chế tối đa việc đoán mò thông tin và tự ý gửi tin nhắn không xin phép.
* **Nhược điểm:** Đôi khi chọn sai `response_type` trong tool `clarify` (ví dụ: dùng `text` thay vì `yes_no`).

#### 3. Phiên bản v2
* **Thay đổi:** Bổ sung quy tắc phân loại `response_type`: dùng `'text'` khi thiếu thông tin, dùng `'yes_no'` khi xin phép xác nhận hành động `send`.
* **Độ chính xác:** Tăng từ 85% lên 90%.
* **Ưu điểm:** Agent gọi `clarify` chuẩn xác hơn, chọn đúng kiểu phản hồi.
* **Nhược điểm:** Một số trường hợp ranh giới bảo mật đối với tool ghi (`send`) vẫn bị lỡ do chỉ dẫn ở `system_prompt.md` quá dài.

#### 4. Phiên bản v3
* **Thay đổi:** Di chuyển luật ranh giới xác nhận (Confirmation Boundary) trực tiếp vào phần `description` của tool `send` trong file `tools.yaml`.
* **Độ chính xác:** Đạt 100% điểm tuyệt đối.
* **Ưu điểm:** Tính nhất quán cực cao. Khi ranh giới của tool được khai báo ngay trong mô tả của chính nó (tool declaration), LLM luôn tuân thủ chặt chẽ hơn.
* **Nhược điểm:** Tăng thêm lượt gọi tương tác đa lượt (multi-turn) để hỏi xác nhận.

## B2. Failure analysis

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R10 | `missing_info` | Tự ý đoán mò thay vì hỏi | Agent không dừng lại hỏi khi thông tin bị thiếu | Thêm chỉ dẫn `clarify` vào System Prompt (`v1`) |
| R11 | `wrong_boundary` | `send(confirmed=true)` | Tự ý gửi Telegram không xin phép user | Yêu cầu hỏi `clarify(response_type='yes_no')` trước khi send (`v1`, `v2`) |
| R12 | `wrong_boundary` | `clarify(response_type='text')` | Chọn sai loại response_type khi xin phép gửi | Khóa boundary trực tiếp vào `tools.yaml` của tool `send` (`v3`) |

## B3. Team eval cases

10 case trong `data/eval_group.json` (5 single-turn, 5 multi-turn) đã được chạy và đạt kết quả điểm **10/10 (100%)** tại phiên bản `v3`:

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| `G01_single_lookup_news_timeframe` | Trích xuất đúng topic="news" và timeframe="day" cho tin tức hôm nay | `lookup(query="OpenAI Sora", topic="news", timeframe="day")` | PASS (100%) |
| `G02_single_timeline_limit` | Map tên người nổi tiếng thành screenname và trích xuất limit=15 | `timeline(screenname="elonmusk", limit=15)` | PASS (100%) |
| `G03_single_out_of_scope` | Từ chối (không dùng tool) đối với yêu cầu nấu ăn ngoài phạm vi tech | Không gọi tool (`no_tool: true`) | PASS (100%) |
| `G04_single_policy_area` | Định tuyến câu hỏi chính sách và chọn đúng policy_area | `policy(policy_area="source_citation")` | PASS (100%) |
| `G05_single_paper_text_pages` | Tải bài báo arXiv kèm giới hạn số trang max_pages=4 | `paper_text(arxiv_url="2401.00001", max_pages=4)` | PASS (100%) |
| `G06_multiturn_clarify_then_send` | Hội thoại 3 lượt: Xác nhận đồng ý gửi bản tin Telegram ở lượt cuối | `send(text="Hello World", confirmed=true)` | PASS (100%) |
| `G07_multiturn_carryover_limit_tweets` | Hội thoại 3 lượt: Đổi tài khoản Twitter nhưng giữ nguyên limit=8 | `timeline(screenname="elonmusk", limit=8)` | PASS (100%) |
| `G08_multiturn_no_tool_meta` | Hội thoại 3 lượt: Thay đổi ý định sang hỏi đáp thông tin bản thân | Không gọi tool (`no_tool: true`) | PASS (100%) |
| `G09_multiturn_switch_policy_area` | Hội thoại 3 lượt: Chuyển đổi chủ đề tra cứu chính sách sang data_privacy | `policy(policy_area="data_privacy")` | PASS (100%) |
| `G10_multiturn_papers_sort_limit` | Hội thoại 3 lượt: Giữ query/limit cũ và thêm sort_by=lastUpdatedDate | `papers(query="Generative AI", max_results=12, sort_by="lastUpdatedDate")` | PASS (100%) |

## B4. Live chat evidence

| Scenario/Turn | Version | Tool Calls + Args | Transcript/Run | Outcome |
|---|---|---|---|---|
| Tra cứu tin tức | v3 | `lookup(query="AI Agents 2026", max_results=3)` | `runs/v3_B_base_openrouter_20260729T103709326371.json` | Trả về thông tin chính xác |
| Xác nhận gửi Telegram | v3 | `clarify(response_type="yes_no")` ➔ `send(confirmed=true)` | `runs/v3_B_group_gemini_20260729T113430960537.json` | Gửi tin nhắn live thành công |

## B5. Tool capability evidence

| Category | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Core Research Tools | `tools/lookup`, `tools/timeline` | Lấy dữ liệu live từ Tavily API và RapidAPI | Cần quản lý API rate limit |
| Action Tool (Telegram) | `tools/send` | Gửi tin nhắn thực tế tới kênh Telegram | Bắt buộc xin xác nhận yes_no |
| **Must-have (Custom Tool 1)** | `tools/dedupe_sources` | Loại bỏ các nguồn trùng lập và làm sạch URL utm tracking | Đảm bảo không xóa nhầm nguồn khác domain |
| **Bonus Custom Tool 2** | `tools/source_quality_check` | Kiểm tra chất lượng metadata, HTTPS và tính hợp lệ của bài viết | Tránh đánh giá sai các URL không dùng HTTPS |
| **Bonus Custom Tool 3** | `tools/extract_citations` | Định dạng tự động trích xuất nguồn theo kiểu numbered/markdown/inline | Không tự động chế tác nguồn giả |
| **Bonus Custom Tool 4** | `tools/filter_sources` | Lọc kết quả nghiên cứu theo domain, từ khóa và tiêu chí HTTPS | Đảm bảo giữ đúng domain được phép |

## B6. Reflection

- **Which fixes belonged in `system_prompt.md`?** Các quy định về hành vi ứng xử chung của Agent (không được tự đoán mò, khi nào cần hỏi lại user, quy tắc định dạng câu trả lời).
- **Which fixes belonged in `tools.yaml`?** Các ranh giới xác nhận nghiêm ngặt (**Confirmation Boundary**) liên quan trực tiếp tới từng Action Tool nhạy cảm.
- **Which failure needed manual review instead of automatic grading?** Các câu trả lời thuộc dạng tổng hợp văn bản hoặc giải thích chi tiết cần đánh giá chất lượng câu từ thay vì chỉ chấm đứt đoạn Tool Calling.
- **What would you improve next?** Bổ sung thêm nhiều tool tích hợp như tra cứu thời tiết, giá tài chính và nâng cấp UI tương tác linh hoạt hơn.
