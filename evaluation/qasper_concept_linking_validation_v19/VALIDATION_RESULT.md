# Kết quả concept-linking validation v19

## Protocol

- 20 paper, 1.029 chunk, 72 câu hỏi QASPER.
- Không trùng 355 paper từng dùng trong development/validation/test trước.
- 72 nhãn được reviewer độc lập hoàn tất và commit ở `bc7ec27` trước prediction.
- 19 câu dương, 53 câu `NONE`, tổng 20 concept assignment.
- Cấu hình cố định: Hybrid concept linking, semantic threshold 0,55.
- Chỉ chạy một threshold và một lần; không chỉnh model/vocabulary theo kết quả.

## Kết quả

| Phương pháp | Precision | Recall | F1 | Exact match |
|---|---:|---:|---:|---:|
| Alias | 1,0000 | 0,2000 | 0,3333 | 0,7917 |
| Semantic | 0,7000 | 0,3500 | 0,4667 | 0,7778 |
| Hybrid | **0,7273** | **0,4000** | **0,5161** | **0,7917** |

Hybrid có 8 true-positive, 3 false-positive và 12 false-negative concept assignment.
57/72 câu có tập prediction khớp hoàn toàn gold label.

## Phân tích lỗi

Nút thắt chính là recall: 12/20 gold assignment bị bỏ sót. Các cách diễn đạt chưa được
khái quát tốt gồm tên nhiệm vụ cụ thể (`dependency parsing`, `EAU`, `error correction`),
tên mô hình (`BERT`, `Relation network`) và diễn đạt gián tiếp (`context similarity
between words`).

Ba false positive là:

1. `back-translation` bị suy rộng thành `TransferLearning`;
2. `macro F1` bị gán thành metric chuyên biệt `EvidenceF1`;
3. câu có `LanguageModel` bị semantic linker gán thêm subtype
   `BidirectionalLanguageModel` không có bằng chứng trực tiếp.

So với development selection v18 (Hybrid F1 0,7200), F1 validation còn 0,5161. Đây là
bằng chứng rằng các cải thiện bằng alias trên development chưa khái quát đủ. Không sửa
alias hoặc threshold bằng v19; vòng cải tiến tiếp theo phải dùng development mới hoặc
phương pháp linking có supervision tốt hơn, sau đó kiểm chứng trên một validation khác.

Final test vẫn niêm phong.

