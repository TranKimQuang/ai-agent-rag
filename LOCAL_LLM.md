# Prototype LLM local

Mặc định vẫn dùng bộ sinh trích xuất. Không gọi API trả phí.
Ollama chỉ được gọi ở 127.0.0.1:11434; không dùng proxy hệ thống.

## Chuẩn bị

Cài Ollama từ https://ollama.com/download/windows rồi mở terminal mới:

```powershell
ollama pull qwen3:4b
ollama list
```

Máy được kiểm tra có khoảng 16 GB RAM và GTX 1650 4 GB. Driver NVIDIA đã
được cập nhật từ 457.34 lên 617.14. Ollama nhận CUDA 13.4 và có thể offload
một phần model Qwen3:4b lên GPU (lần kiểm tra gần nhất: khoảng 67% GPU,
33% CPU). Lần gọi đầu sau khi nạp model vẫn có thể chậm hơn đáng kể.
Không cài CUDA toolkit hoặc PostgreSQL cho bước này.

## Smoke test độc lập

Tại thư mục ai-agent-rag:

```powershell
.\.venv\Scripts\python.exe -m scripts.smoke_local_llm
```

10 câu hỏi dùng evidence tổng hợp cố định; 7 có đáp án, 3 thiếu thông tin.
Đây chỉ kiểm tra phần sinh câu trả lời, không đo retrieval/QASPER.
Kết quả mới lưu results/local_llm_sentence_ids_<timestamp>.json, không ghi đè
kết quả thử ban đầu. Các cột chấm ngữ nghĩa để null
cho đến khi người đọc kiểm tra. Không coi quote hợp lệ là câu trả lời đúng.

## Bật ở API

```powershell
$env:ANSWER_BACKEND = 'ollama'
$env:OLLAMA_MODEL = 'qwen3:4b'
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Dừng server cũ trước khi chạy cùng cổng. Nạp lại PDF nếu chỉ mục RAM đã mất.
POST /ask giữ nguyên request. Mỗi ý trả lời có số nguồn [1], [2]...
Metadata tên file/trang được lấy từ server, không tin metadata model tự viết.
Model chỉ chọn sentence_id từ các câu được server cấp; không tự chép quote.
Server tự lấy nguyên văn câu được chọn và metadata của chunk chứa câu đó.
Model từ chối: insufficient_evidence. ID sai/claim rỗng: HTTP 503 (lỗi output),
không giả thành thiếu bằng chứng. ID chỉ có hiệu lực trong request hiện tại.
Mất kết nối, JSON lỗi, timeout hoặc sinh dở: HTTP 503; không giả thành thiếu evidence.

Để quay về chế độ cũ, đặt ANSWER_BACKEND=extractive rồi khởi động lại server.

## Giới hạn

- Chỉ gửi tối đa 3 chunk, mỗi chunk 1800 ký tự; context 4096, output 700 token.
- Kiểm tra ID hợp lệ không chứng minh claim được evidence hỗ trợ.
- Evidence gate hiện là heuristic chưa hiệu chỉnh cho answerability; confidence
  trong API không phải xác suất câu trả lời đúng.
- Prompt yêu cầu bỏ qua chỉ dẫn trong tài liệu không bảo đảm chống prompt injection.
- Đã chạy smoke model thật trên cả CPU và GPU; xem LOCAL_LLM_SMOKE_REPORT.md.
  Đây mới là phép thử nhỏ trên evidence tổng hợp, chưa phải đánh giá LLM trên
  QASPER và chưa đo peak RAM/VRAM.
- Không thay đổi hay chạy lại retrieval held-out để lựa chọn model.
