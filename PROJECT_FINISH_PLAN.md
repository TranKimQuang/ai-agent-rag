# Kế hoạch hoàn thành đồ án

Ngày khóa phạm vi: 20/10/2026

## 1. Kết luận về phạm vi

Dự án vẫn đúng hướng giảng viên yêu cầu: Ontology phục vụ retrieval và giải thích,
ablation trên QASPER thật, cùng prototype Answer Agent có evidence gate và citation.
Tuy nhiên, quá trình nghiên cứu đã bị phức tạp hóa bởi quá nhiều phiên bản dữ liệu và
thử nghiệm concept-linking nhỏ. Từ mốc này không tạo thêm v23/v24, không tiếp tục đổi
vocabulary/threshold theo các tập đã xem và không chạy lại held-out để chọn mô hình.

## 2. Phần đã đủ

| Yêu cầu chính | Trạng thái | Bằng chứng chuẩn |
|---|---|---|
| Ontology mở rộng, relation, Result và CSO mapping | Hoàn thành | `ontology/document_qa.owl`, `ontology/document_qa.ttl`, `ONTOLOGY_QUALITY_REPORT.md` |
| Concept linking alias và semantic | Hoàn thành ở mức prototype nghiên cứu | `evaluation/qasper_concept_labeling_development_v18/`, `evaluation/qasper_taxonomy_concept_development_v22/` |
| Ablation trên dữ liệu QASPER thật | Hoàn thành | `evaluation/qasper_train_v3/heldout_result_once.json` |
| Kiểm tra khả năng khái quát | Hoàn thành, kết quả âm | Held-out v3: Hybrid và re-ranking hòa nhau; expansion kém hơn |
| Answer Agent, evidence gate và citation | Hoàn thành ở mức prototype | `QASPER_ANSWER_EVALUATION.md`, `results/qasper_answer_evaluation_20260928T085754Z.json` |
| Câu hỏi unanswerable | Có thử nghiệm ban đầu | Agent từ chối đúng 2/2 câu tự nhiên trong mẫu 52 case |
| Giao diện demo và API | Hoàn thành | `/`, `/docs`, `/ask`, `/search` |

## 3. Kết quả chính phải báo cáo trung thực

### Retrieval held-out v3 — 70 câu, chạy đúng một lần

| Phương pháp | Recall@5 | MRR@5 | nDCG@5 |
|---|---:|---:|---:|
| BM25 | 0,2219 | 0,1336 | 0,1459 |
| Semantic | 0,1929 | 0,1319 | 0,1422 |
| Hybrid | 0,2629 | 0,1448 | 0,1722 |
| Hybrid + Ontology re-ranking | 0,2629 | 0,1448 | 0,1722 |
| Hybrid + Ontology expansion | 0,2356 | 0,1269 | 0,1456 |

Kết luận: Ontology đã được tích hợp thật và cải thiện trên development, nhưng không
khái quát trên held-out vì chỉ 6/70 query nhận được concept và chỉ 5/70 cặp
query/evidence có quan hệ Ontology. Đây là kết quả nghiên cứu hợp lệ, không phải lỗi cần
che hoặc tiếp tục tuning theo test.

### Answer Agent development — 50 answerable + 2 unanswerable

- Answer-F1: 0,314.
- Evidence-F1: 0,307.
- Citation precision/recall: 0,317/0,290.
- Trả lời 40/50 câu answerable.
- Từ chối đúng 2/2 câu unanswerable tự nhiên.
- Đây là kết quả development và prototype, không gọi là held-out cuối.

## 4. Checklist về đích

- [x] Khóa code, Ontology và cấu hình retrieval hiện tại.
- [x] Giữ nguyên held-out v3 đã chạy; không chạy lại hoặc tuning theo kết quả này.
- [x] Ghi nhận kết quả âm của projection cha–con trên development v22.
- [x] Tạo một bảng tổng hợp cuối duy nhất từ các artifact đã có; không chạy thêm model
  (`FINAL_EXPERIMENT_SUMMARY.md`).
- [x] Chọn năm ví dụ QASPER thật: ba trường hợp re-ranking cải thiện và hai trường
  hợp làm xấu thứ hạng/query drift.
- [x] Đồng bộ Google Docs với kết quả held-out v3, Answer Agent 52 case, kế hoạch khóa
  phạm vi và phân tích định tính.
- [x] Chạy toàn bộ test: 205 test passed, Ruff passed; còn một cảnh báo deprecation
  Starlette/httpx không làm thay đổi kết quả.
- [x] Tạo tag `ontology-agent-report-v2` cho mốc báo cáo đã kiểm thử.

## 5. Việc dừng làm

- Không tạo thêm phiên bản dataset chỉ để thử threshold/linker mới.
- Không mở rộng vocabulary nếu không có giả thuyết và dữ liệu độc lập.
- Không triển khai PostgreSQL, pgvector, OCR hoặc Agent framework phức tạp.
- Không làm lại giao diện ngoài sửa lỗi ảnh hưởng demo.
- Không tuyên bố Ontology cải thiện held-out; chỉ trình bày đúng development gain và
  held-out negative result.

## 6. Điều kiện coi là hoàn thành

Đồ án được coi là hoàn thành về kỹ thuật khi checklist mục 4 được đóng. Chất lượng
nghiên cứu không phụ thuộc vào việc Ontology bắt buộc phải thắng baseline; đóng góp là
pipeline có thể kiểm chứng, ablation rõ ràng, phân tích coverage/query drift và cơ chế
Agent từ chối khi evidence không đủ.

