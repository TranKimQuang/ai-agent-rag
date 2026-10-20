# Tổng hợp thực nghiệm cuối

Ngày tổng hợp: 20/10/2026

Tài liệu này chọn một nguồn chuẩn cho mỗi kết luận. Nó không chạy lại model và không
thay đổi cấu hình sau khi đã xem held-out.

## 1. Retrieval ablation trên QASPER thật

### Development v3 — 78 câu

| Phương pháp | Recall@5 | MRR@5 | nDCG@5 |
|---|---:|---:|---:|
| BM25 | 0,2781 | 0,2026 | 0,2059 |
| Semantic | 0,2379 | 0,1761 | 0,1785 |
| Hybrid | 0,2991 | 0,2331 | 0,2306 |
| Hybrid + Ontology expansion | 0,2703 | 0,2274 | 0,2144 |
| Hybrid + Ontology re-ranking | 0,2991 | 0,2331 | 0,2306 |
| Hybrid + Expansion + Re-ranking | 0,2703 | 0,2274 | 0,2144 |

Sau khi mở rộng vocabulary có kiểm soát, re-ranking đạt Recall@5 0,3120,
MRR@5 0,2385 và nDCG@5 0,2371. Trọng số 0,05 được chọn chỉ trên development;
expansion tiếp tục gây query drift và bị tắt trong cấu hình khóa.

Nguồn chuẩn:

- `evaluation/qasper_train_v3/development_retrieval_results.json`
- `evaluation/qasper_train_v3/development_retrieval_after_vocabulary.json`
- `evaluation/qasper_train_v3/locked_retrieval_config_v3.json`

### Held-out v3 — 70 câu, chạy đúng một lần

| Phương pháp | Recall@5 | MRR@5 | nDCG@5 |
|---|---:|---:|---:|
| BM25 | 0,2219 | 0,1336 | 0,1459 |
| Semantic | 0,1929 | 0,1319 | 0,1422 |
| Hybrid | **0,2629** | **0,1448** | **0,1722** |
| Hybrid + Ontology re-ranking | **0,2629** | **0,1448** | **0,1722** |
| Hybrid + Ontology expansion | 0,2356 | 0,1269 | 0,1456 |

Nguồn chuẩn: `evaluation/qasper_train_v3/heldout_result_once.json`.

Kết luận khái quát: re-ranking hòa Hybrid và expansion kém hơn. Chỉ 6/70 query
nhận được concept và 5/70 cặp query/evidence có quan hệ Ontology. Ontology có tác
động trên development nhưng coverage chưa đủ để cải thiện dữ liệu chưa thấy.

Không chạy nhánh “Expansion + Re-ranking” trên held-out sau khi đã biết expansion
gây hại; bảng ablation đầy đủ của nhánh này được giữ ở development. Không chạy lại
held-out để bổ sung một ô còn thiếu vì việc đó vi phạm giao thức one-time test.

## 2. Concept linking và taxonomy diagnostic

Development v22 gồm 40 câu QASPER thật, 37 paper, với 17 concept assignment đã khóa
trước prediction. Nhãn là Qwen3:4b review mù rồi assistant audit, không phải human gold.

| Phạm vi | Whole-query F1 | Phrase-first F1 |
|---|---:|---:|
| Toàn vocabulary | 0,5714 | 0,5789 |
| 22 concept taxonomy được gán nhãn | 0,7407 | 0,7586 |

Không có prediction–gold nào là quan hệ cha–con trực tiếp; taxonomy-aware F1 bằng
exact F1. Vì vậy chưa có bằng chứng để triển khai projection cha–con.

Nguồn chuẩn: `evaluation/qasper_taxonomy_concept_development_v22/RESULT_SUMMARY.md`.

## 3. Answer Agent development

Mẫu mở rộng gồm 50 câu answerable và 2 câu strict natural unanswerable từ 20 paper
QASPER development. Pipeline: document-scoped Hybrid + Ontology re-ranking, evidence
gate, Qwen3:4b local và citation do server kiểm soát.

| Chỉ số | Kết quả |
|---|---:|
| Answer-F1 trên 50 câu answerable | 0,314 |
| Evidence-F1 | 0,307 |
| Citation precision | 0,317 |
| Citation recall | 0,290 |
| Câu được trả lời | 40/50 |
| Unanswerable từ chối đúng | 2/2 |
| Generation error | 0 |
| Thời gian trung bình | 10,077 giây/câu |

Nguồn chuẩn:

- `QASPER_ANSWER_EVALUATION.md`
- `results/qasper_answer_evaluation_20260928T085754Z.json`

Đây là development evidence cho prototype, không phải held-out Answer Agent. Thử mở
rộng context từ 3 lên 5 chunk tăng Answer-F1 lên 0,366 nhưng làm tỷ lệ từ chối đúng
unanswerable giảm từ 2/2 xuống 1/2; vì vậy 3 chunk vẫn là mặc định an toàn.

## 4. Kết luận dùng trong báo cáo

1. Pipeline Ontology-aware RAG và Agent đã được triển khai end-to-end trên dữ liệu thật.
2. Ontology re-ranking tạo cải thiện nhỏ trên development nhưng không vượt Hybrid trên
   held-out; nguyên nhân chính là concept coverage thấp trên chủ đề chưa thấy.
3. Query expansion gây query drift trong cả development và held-out nên không được bật
   mặc định.
4. Agent sinh được câu trả lời có citation và biết từ chối khi evidence yếu, nhưng
   retrieval/evidence selection vẫn là giới hạn chính.
5. Đóng góp phù hợp của đồ án là kiến trúc có thể kiểm chứng, mô hình Ontology/CSO,
   ablation tách thành phần và phân tích failure mode; không tuyên bố Ontology luôn cải
   thiện RAG.

## 5. Giới hạn

- Concept-label development chưa phải human gold chính thức.
- Mẫu unanswerable của Agent chỉ có hai câu, chưa đủ cho ước lượng ổn định.
- Answer Agent chưa có held-out cuối riêng; kết quả 52 case chỉ dùng cho prototype.
- QASPER gold evidence có thể không đầy đủ và token F1 không đo hết đúng nghĩa.

