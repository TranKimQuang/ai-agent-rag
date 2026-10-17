# Adjudicated concept-label report (development v18)

## Quy trình

1. Audit nội bộ 112 câu.
2. Thread LLM độc lập gán nhãn mù đủ 112 câu bằng catalog đang hoạt động.
3. Hai bên đồng thuận 92/112 câu; 20 câu bất đồng được một reviewer LLM thứ ba phân xử
   theo policy đã khóa trước.
4. Không reviewer nào được xem kết quả benchmark khi gán nhãn/phân xử.

Đây là nhãn đã **LLM-adjudicated**, chưa được gọi là human gold.

## Nhãn sau phân xử

- Toàn bộ pool: 112 câu, 25 câu dương và 87 câu `NONE`.
- Selection development: 55 câu, 15 câu dương.
- Internal verification: 57 câu, 10 câu dương; không chạy lại benchmark trên phần này.

## Benchmark selection sau phân xử

Kết quả đầu tiên trên policy nhãn cuối cho thấy alias cũ quá rộng:

| Phương pháp | Precision | Recall | F1 | Exact match |
|---|---:|---:|---:|---:|
| Alias cũ | 0,583 | 0,467 | 0,519 | 0,764 |
| Semantic 0,55 | 0,833 | 0,333 | 0,476 | 0,800 |
| Hybrid cũ 0,55 | 0,600 | 0,600 | 0,600 | 0,782 |

Bốn câu dùng “embedding(s)” chung và một câu dùng “paired corpora” bị gán subtype quá
cụ thể. Vì các lỗi này lặp lại trên selection, alias chung `embedding/embeddings` của
`WordEmbedding` và `paired corpus/corpora` của `ParallelCorpus` được loại. Các alias cụ
thể `word embedding(s)` và `parallel corpus/corpora` vẫn giữ.

Sau refinement và sweep 0,50-0,70 trên selection:

| Phương pháp | Precision | Recall | F1 | Exact match |
|---|---:|---:|---:|---:|
| Alias | **1,000** | 0,467 | 0,636 | 0,855 |
| Semantic 0,55 | 0,833 | 0,333 | 0,476 | 0,800 |
| Hybrid 0,55 | 0,900 | **0,600** | **0,720** | **0,873** |

Hybrid 0,55 tiếp tục được chọn. So với trước refinement, F1 tăng từ 0,600 lên 0,720 do
loại 5 false positive; Recall không đổi. Không thêm alias BERT dù adjudicator chấp nhận
hai nhãn BERT, vì cả hai câu nằm trong internal verification đã khóa.

## Kết luận

Kết quả F1 0,720 thấp hơn con số 0,800 trước independent review, nhưng đáng tin cậy hơn:
nhãn cũ đã ưu ái các alias do chính pipeline tạo. Nút thắt còn lại là Recall trên các
paraphrase như dialogue acts, natural-language agents, pivot language và distributional
methods. Không tiếp tục tuning bằng 57 câu verification.

Artifacts:

- `third_reviewer_adjudication_20.json`
- `adjudicated_concept_labels_112.json`
- `adjudicated_selection_55.json`
- `adjudicated_selection_55_benchmark.json`
- `adjudicated_selection_55_after_alias_refinement.json`
