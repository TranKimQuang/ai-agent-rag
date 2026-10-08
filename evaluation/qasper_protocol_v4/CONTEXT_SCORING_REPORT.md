# Context-aware Ontology scoring v1

## Thay đổi

Phiên bản này không thêm concept hoặc alias mới. Ontology score được điều chỉnh theo:

1. quan hệ exact/related/type trong knowledge graph;
2. loại thực thể mà câu hỏi yêu cầu (`Method`, `Model`, `Dataset`, `Metric`, `Task`);
3. concept có xuất hiện rõ trong câu hỏi và passage hay chỉ được semantic linker suy ra;
4. độ đặc hiệu của concept, giảm ảnh hưởng của các hub rộng;
5. độ mạnh của retrieval gốc.

Điểm Ontology không còn được nội suy độc lập với RRF. Nó trở thành bonus nhân trên điểm
retrieval đã chuẩn hóa, vì vậy một passage yếu không thể lên đầu chỉ do chứa concept rộng.

## Development (74 câu)

| Cấu hình | Recall@5 | MRR@5 | nDCG@5 | Thay đổi hạng |
|---|---:|---:|---:|---|
| Hybrid | 0,3027 | 0,2074 | 0,2113 | Baseline |
| Context score, weight 0,10 | 0,3027 | 0,2200 | 0,2211 | 2 tốt hơn, 0 xấu hơn |
| Context score, weight 0,40 | 0,3054 | 0,2110 | 0,2202 | 2 tốt hơn, 1 xấu hơn |

Development cho thấy context score có tín hiệu tốt hơn công thức cố định cũ, đặc biệt ở
MRR/nDCG, nhưng số câu thực sự đổi hạng vẫn nhỏ.

## Validation (35 câu)

Các weight `0; 0,05; 0,10; 0,20; 0,30; 0,40; 0,50; 0,75; 1,00` đều giữ nguyên
Recall@5 `0,1857`, MRR@5 `0,1929` và nDCG@5 `0,1689`; không có câu nào đổi hạng.

Do validation không chứng minh được cải thiện, cấu hình được chọn vẫn là Hybrid với
Ontology weight `0,0`. Final-test tiếp tục ở trạng thái `sealed_not_evaluated`.

## Kết luận

Context-aware scoring v1 đã giải quyết rủi ro chính của công thức cũ: Ontology không còn
tự kéo passage yếu lên trên chỉ vì concept match. Tuy nhiên, coverage và độ phân biệt trên
validation vẫn chưa đủ. Không được dùng kết quả development để tự ý bật weight `0,10` hoặc
`0,40` cho final-test.
