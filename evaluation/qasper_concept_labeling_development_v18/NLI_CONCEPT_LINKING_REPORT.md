# NLI concept-linking experiment (development v18)

## Mục tiêu và giao thức

Thử dùng NLI để xác nhận các semantic candidate mà alias không nhận diện được. Thử nghiệm
chỉ dùng 55 câu selection của development v17 cùng overlay nhãn đã audit; 57 câu internal
verification được giữ nguyên và không chạy lại.

- Model: `cross-encoder/nli-deberta-v3-small`.
- Thiết bị: CPU.
- Candidate: Top-5 semantic candidate cho từng cụm từ, không áp ngưỡng trước NLI.
- Điểm dùng để quyết định: xác suất nhãn `entailment`; thứ tự nhãn của model là
  `contradiction`, `entailment`, `neutral`.
- Sweep ngưỡng entailment: 0,40-0,80; margin: 0,00-0,20.
- Tiêu chí chọn: F1, sau đó Precision và exact match.

## Kết quả

| Phương pháp | Precision | Recall | F1 | Exact match |
|---|---:|---:|---:|---:|
| Alias | 1,000 | 0,600 | 0,750 | 0,855 |
| Semantic | 0,833 | 0,250 | 0,385 | 0,709 |
| Hybrid (ngưỡng 0,55) | **0,933** | 0,700 | **0,800** | **0,873** |
| Phrase-first hiện tại | 0,607 | **0,850** | 0,708 | 0,782 |
| NLI tốt nhất (threshold 0,80; margin 0,20) | 0,308 | 0,600 | 0,407 | 0,527 |

## Kết luận

Không đưa NLI candidate gate vào pipeline. Dù tăng khả năng nhận diện diễn đạt không trùng
alias, model NLI tổng quát không phân biệt đủ tốt các khái niệm kỹ thuật gần nhau và tạo
nhiều false positive. Kết quả kém Hybrid 0,393 F1 và kém 0,346 exact match.

Giữ Hybrid ngưỡng 0,55 làm candidate hiện tại. Không tuning theo 57 câu internal
verification. Bước tiếp theo không phải mở rộng vocabulary hoặc thêm tầng NLI, mà là:

1. Nhờ người thứ hai xác nhận độc lập 28 nhãn dương và một mẫu câu âm.
2. Từ nhãn đã xác nhận, tạo train/development theo paper và thử linker có supervision
   trực tiếp cho taxonomy của dự án.
3. Chỉ mở validation paper-disjoint mới khi candidate mới vượt Hybrid trên development.

Artifact máy đọc:

- `audited_selection_55_baseline.json`
- `nli_selection_55_results.json`

Phép thử supervised paper-disjoint tiếp theo cũng không vượt baseline; xem
`SUPERVISED_CONCEPT_LINKING_REPORT.md`.
