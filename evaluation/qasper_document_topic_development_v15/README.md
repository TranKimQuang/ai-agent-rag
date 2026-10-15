# Document-topic prior development v15

## Mục tiêu

Kiểm tra liệu chủ đề của đúng bài báo nguồn có giúp semantic query linking và Ontology
re-ranking chính xác hơn hay không. Thí nghiệm chỉ dùng development v10 gồm 20 paper,
824 chunk và 74 câu hỏi; không mở lại validation v13 hay final-test.

## Thiết kế

Ba cấu hình giữ nguyên BM25, embedding, RRF, phrase-first linking, threshold query 0,55,
threshold chunk 0,65 và Ontology weight 0,20. Biến duy nhất là document-topic prior:

1. `baseline`: không dùng prior.
2. `first-3`: lấy concept từ ba chunk đầu, cộng 0,05 cho concept cùng/quan hệ một bước
   và trừ 0,05 cho concept ngoài hồ sơ.
3. `full-document`: dùng cùng công thức nhưng lập hồ sơ từ toàn bộ chunk của bài báo.

Exact alias không bị điều chỉnh. Tính năng mặc định vẫn tắt.

## Kết quả k=5

| Cấu hình / phương pháp | Recall@5 | MRR@5 | nDCG@5 |
|---|---:|---:|---:|
| Hybrid baseline | 0,6164 | 0,3818 | 0,4140 |
| Phrase-first Expansion + Re-ranking, không prior | 0,5928 | 0,3466 | 0,3875 |
| First-3 Expansion + Re-ranking | 0,5894 | 0,3390 | 0,3762 |
| Full-document Expansion + Re-ranking | 0,5793 | 0,3338 | 0,3746 |
| Phrase-first Re-ranking, không prior | 0,6164 | 0,3800 | 0,4136 |
| **Full-document Re-ranking only** | **0,6164** | **0,3840** | **0,4158** |

First-3 làm query coverage giảm từ 17/74 xuống 13/74 và làm mất quan hệ đúng của câu
về chất lượng tóm tắt. Candidate này bị loại. Full-document prior cũng làm query expansion
drift mạnh hơn nên Expansion và bản kết hợp đều bị loại.

Riêng full-document + re-ranking cải thiện hai câu, làm xấu một câu, giữ Recall@5 và tăng
MRR@5 thêm 0,0023, nDCG@5 thêm 0,0018 so với Hybrid. Paired bootstrap 10.000 mẫu cho
MRR có CI 95% [-0,0041; +0,0108], p=0,6485; nDCG có CI [-0,0034; +0,0087],
p=0,6517. Hướng thay đổi dương nhưng chưa có ý nghĩa thống kê.

## Quyết định

- Không bật document-topic prior trong pipeline chính.
- Giữ hạ tầng dưới cờ cấu hình tắt mặc định và giữ toàn bộ artifact âm để tránh lặp lại.
- Nếu kiểm chứng tiếp, chỉ xem xét `Hybrid + full-document topic prior re-ranking`, không
  dùng prior cho query expansion; cần một validation paper-disjoint mới trước khi kết luận.
