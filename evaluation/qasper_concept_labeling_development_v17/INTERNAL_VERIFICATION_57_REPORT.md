# Internal verification concept linking trên 57 câu dự trữ

## Protocol

Cấu hình được khóa và push ở commit `d1d49c4` trước khi chạy prediction:

- method: Hybrid;
- semantic threshold: 0,55;
- Phrase-first: tắt;
- ontology TTL blob: `efc54bfaf9ab8284680d86c28188cb2dde9cfdb4`;
- ontology OWL blob: `ef661922dbc889406ddfe8c0603a7eebd652f033`.

Toàn bộ 57 câu được gán nhãn trước prediction, không trùng 55 câu đã dùng để chọn cấu
hình. Tập dự trữ có 10 nhãn dương và 47 câu âm. Nó được chạy đúng một lần, chỉ tại ngưỡng
đã khóa 0,55; không sweep threshold và không chạy Phrase-first.

Nhãn vẫn có trạng thái `assistant_pre_review`, vì vậy kết quả cần được xác nhận thủ công
trước khi dùng trong báo cáo chính thức.

Audit riêng ngày 17/10/2026 đã kiểm tra 10 nhãn dương: giữ 7 và loại 3 nhãn gán quá
rộng (`ArgumentMining` cho câu hỏi người thắng tranh luận và hai ánh xạ BERT sang
`BidirectionalLanguageModel`). Xem `INTERNAL_VERIFICATION_POSITIVE_LABEL_AUDIT.md` và
`internal_verification_positive_label_audit.json`. Artifact prediction khóa không được
chạy lại hoặc sửa hồi tố.

## Kết quả một lần duy nhất

| Phương pháp | Precision | Recall | F1 | Exact match |
|---|---:|---:|---:|---:|
| Alias | 0,000 | 0,000 | 0,000 | 0,789 |
| Semantic | 0,000 | 0,000 | 0,000 | 0,772 |
| Hybrid | 0,000 | 0,000 | 0,000 | 0,737 |

Không phương pháp nào tìm đúng một trong 10 nhãn dương dự trữ. Từ exact match có thể xác
định Alias làm sai thêm 2 câu âm, Semantic 3 câu âm và Hybrid 5 câu âm, ngoài 10 câu
dương bị bỏ sót. Artifact hiện tại chỉ lưu metric tổng hợp; không chạy lại tập dự trữ để
lấy prediction từng hàng.

## Diễn giải

Kết quả 55 câu dùng để lựa chọn (Hybrid F1 0,811) không khái quát sang 57 câu còn lại.
Các nhãn dương dự trữ chủ yếu là paraphrase khó hoặc khái niệm cấp cao, ví dụ:

- `BERT` → `BidirectionalLanguageModel`;
- `code-switching`/`language families` → `MultilingualNaturalLanguageProcessing`;
- `perplexity` → `LanguageModel`;
- `NER`, cú pháp và hypernymy → `NaturalLanguageProcessing`;
- câu hỏi về người thắng tranh luận → `ArgumentMining`.

Sentence-transformer hiện tại không đủ ổn định cho các liên kết kiểu này ở ngưỡng an
toàn. Giảm threshold có nguy cơ lặp lại false positive đã thấy trên development 55 câu.

## Quyết định

- Không thay alias, threshold hoặc ontology theo 57 câu dự trữ.
- Không mở validation paper-disjoint mới ở trạng thái hiện tại.
- Giữ kết quả âm để báo cáo trung thực giới hạn khả năng khái quát.
- Trước thử nghiệm tiếp theo, cần xác nhận thủ công các nhãn `assistant_pre_review`.
- Đã audit tiếp 102 nhãn còn lại; toàn bộ 112 câu hiện ở trạng thái assistant-audited
  nhưng chưa phải gold do người gán nhãn độc lập xác nhận.
- Sau khi nhãn được xác nhận, phát triển một candidate linker mới chỉ trên 55 câu selection
  hoặc tạo development mới; 57 câu này không được dùng tiếp để chọn mô hình.

Do verifier hiện chỉ lưu metric tổng hợp, lần validation độc lập kế tiếp phải xuất prediction
từng câu ngay trong lần chạy đầu tiên để có error analysis mà không cần chạy lại.
