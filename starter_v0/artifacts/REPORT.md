# Day 04 Lab v2 Report — Research Agent

> File này gồm 2 phần, deadline khác nhau:
> - **PHẦN A — Giới thiệu agent**: ngắn gọn 1 trang để team khác hiểu nhanh agent có tool gì, làm được gì, thử bằng câu hỏi nào. Xong trước 11:30 để làm tài liệu phụ trợ khi demo.
> - **PHẦN B — Chi tiết / Bằng chứng**: bảng đầy đủ (v0–v3, failure, eval, chat) dựa trên log thật. Có thể hoàn thiện sau buổi debate để nộp bài.

## Team

- Team:
- Members:
- Provider/model:

---

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

> 1–2 câu mô tả agent dùng để làm gì.

Ví dụ: "Research agent: tìm tin theo từ khóa / theo tài khoản, đọc URL và tổng hợp thành digest."

**Link dùng thử (truy cập được trong showdown):**

> Dán public URL nếu người khác cần mở từ máy riêng; localhost cũng được nếu demo trực tiếp trên máy trình chiếu. Streamlit được khuyến nghị, nhưng nhóm có thể dùng bất kỳ framework nào.
>
> URL:

## A2. Tool agent có

> Liệt kê các tool agent đang dùng. Mỗi tool 1 dòng: tên + làm được gì.

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | hỏi lại người dùng khi thiếu thông tin | không |
|  |  |  |
|  |  |  |

## A3. Câu hỏi mẫu để thử

> 3–5 câu hỏi/yêu cầu mẫu để team khác tự thử agent ngay.

1.
2.
3.

## A4. Kịch bản demo đã rehearse

> Chuẩn bị 3–5 scenario. Mỗi scenario cần cho thấy tool đã làm gì và một thay đổi cụ thể giữa các version.

| Scenario | Tool trace cần thấy | Câu chuyện cải thiện version | Fallback run/transcript |
|---|---|---|---|
|  |  |  |  |

---

# PHẦN B — Chi tiết / Bằng chứng

> Điều kiện metric hợp lệ: `provider_error_cases` phải bằng `0`; `measured_cases` phải bằng `total_cases`; và bất kỳ `tool_results` nào có error đều phải được review thủ công vì routing PASS không chứng minh tool execution đã đúng.

## B1. Version evidence

Fill from `artifacts/version_log.csv` and `runs/*.json`.

| Version | Prompt/tool change | Hypothesis | Metric name | Before | After | Run File |
|---|---|---|---|---:|---:|---|
| v0 | baseline |  |  |  |  |  |
| v1 |  |  |  |  |  |  |
| v2 |  |  |  |  |  |  |
| v3 |  |  |  |  |  |  |

## B2. Failure analysis

Use actual failures from `results[*].result.failures`.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
|  |  |  |  |  |

## B3. Team eval cases

List the 10 cases added to `data/eval_group.json`:

- 5 single-turn
- 5 multi-turn

This section is for the mandatory team-authored eval set. Optional built-ins do
not belong here.

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| `G01_single_lookup_news_timeframe` | Kiểm tra trích xuất đúng topic="news" và timeframe="day" cho tin tức hôm nay | `lookup(query="OpenAI Sora", topic="news", timeframe="day")` | PASS |
| `G02_single_timeline_limit` | Kiểm tra map tên người nổi tiếng thành screenname và trích xuất đúng limit | `timeline(screenname="elonmusk", limit=15)` | PASS |
| `G03_single_out_of_scope` | Kiểm tra từ chối (không dùng tool) đối với yêu cầu ngoài phạm vi công nghệ | Không gọi tool (`no_tool: true`) | PASS |
| `G04_single_policy_area` | Kiểm tra định tuyến câu hỏi chính sách và chọn đúng policy_area | `policy(policy_area="source_citation")` | PASS |
| `G05_single_paper_text_pages` | Kiểm tra tải nội dung bài báo arXiv kèm giới hạn số trang đọc | `paper_text(arxiv_url="2401.00001", max_pages=4)` | PASS |
| `G06_multiturn_clarify_then_send` | Hội thoại 3 lượt: Xác nhận đồng ý gửi bản tin lên Telegram ở lượt cuối | `send(text="Hello World", confirmed=true)` | PASS |
| `G07_multiturn_carryover_limit_tweets` | Hội thoại 3 lượt: Đổi tài khoản Twitter đích nhưng giữ nguyên số lượng limit | `timeline(screenname="elonmusk", limit=8)` | PASS |
| `G08_multiturn_no_tool_meta` | Hội thoại 3 lượt: Thay đổi ý định sang hỏi đáp về khả năng của hệ thống | Không gọi tool (`no_tool: true`) | PASS |
| `G09_multiturn_switch_policy_area` | Hội thoại 3 lượt: Chuyển đổi chủ đề tra cứu chính sách công ty ở lượt cuối | `policy(policy_area="data_privacy")` | PASS |
| `G10_multiturn_papers_sort_limit` | Hội thoại 3 lượt: Đọc cấu hình tìm bài báo, áp dụng sắp xếp và lưu các bộ lọc cũ | `papers(query="Generative AI", max_results=12, sort_by="lastUpdatedDate")` | PASS |

## B4. Live chat evidence

Use `transcripts/*.transcript.json`.

| Scenario/Turn | Version | Tool Calls + Args | Transcript/Run | Outcome |
|---|---|---|---|---|
|  |  |  |  |  |

## B5. Tool capability evidence

Phân loại rõ tool mới bắt buộc, optional built-in và tool đủ điều kiện bonus. Chỉ ghi Telegram/PDF nếu nhóm thực sự dùng; base report không cần chúng.

UI is core deliverable, not bonus. Do not list it here.

| Category | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Must-have: tool mới đầu tiên |  |  |  |
| Optional built-in |  |  |  |
| Bonus: tool mới thứ 4 trở đi |  |  |  |

## B6. Reflection

- Which fixes belonged in `system_prompt.md`?
- Which fixes belonged in `tools.yaml`?
- Which failure needed manual review instead of automatic grading?
- What would you improve next?
