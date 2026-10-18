# QASPER concept-linking development v20

## Dữ liệu

- 30 paper, 1.694 chunk và 43 câu hỏi có gold evidence.
- Không trùng với 375 paper đã dùng trước v20.
- Do phần QASPER train còn lại chỉ có 10 paper đạt tối thiểu 3 câu, protocol dùng tối
  thiểu 1 câu/paper để giữ 30 paper đa dạng và paper-disjoint.
- Reviewer độc lập gán 17 câu dương, 26 câu `NONE`, tổng 19 concept assignment.

## Baseline v20

Hybrid tốt nhất ở threshold 0,65 nhưng bằng Alias: Precision 0,7143, Recall 0,2632,
F1 0,3846 và exact match 0,7209. Semantic whole-query không cải thiện recall đủ để bù
false positive.

## Candidate trên development gộp

Gộp 55 câu selection v18 và 43 câu v20 thành 98 câu/55 paper, 34 gold assignment.
Mọi đánh giá supervised dùng GroupKFold tách theo paper.

| Candidate | Precision | Recall | F1 | Exact match |
|---|---:|---:|---:|---:|
| Hybrid whole-query 0,60 | 0,8125 | 0,3824 | 0,5200 | **0,8061** |
| Supervised + Alias | **0,8571** | 0,3529 | 0,5000 | 0,7959 |
| Phrase-first 0,65, margin 0,03 | 0,7500 | **0,4412** | **0,5556** | 0,7959 |

Phrase-first cũng cải thiện F1 riêng trên cả hai pool: v18 từ 0,6364 lên 0,6667 và v20
từ 0,3846 lên 0,4444. Vì vậy đây là candidate được khóa để kiểm chứng trên validation
paper-disjoint mới. Supervised logistic regression chưa được chọn vì 9/14 concept vẫn
chỉ có 1-2 ví dụ và F1 không vượt Hybrid.

Không dùng validation v19 để chỉnh candidate; final test vẫn niêm phong.

