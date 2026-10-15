# Document-topic prior validation v16

## Protocol

- 20 QASPER paper, 1.494 chunk, 77 câu hỏi có gold evidence.
- Không trùng với 305 paper trong các development/validation/final-test trước.
- Dataset SHA-256: `8e172b89c3d64de265bce247b97f0e12405766b489acbf4a4f9e3c4e208dc5eb`.
- Candidate code: commit `38ccd4e`.
- Candidate được chọn duy nhất từ development v15.

## Candidate đã khóa

So sánh chính là Hybrid với Hybrid + Ontology re-ranking. Query dùng phrase-first
semantic linking; prior lấy concept từ toàn bộ bài báo nguồn, cộng 0,05 cho semantic
candidate được hồ sơ bài báo hỗ trợ và trừ 0,05 cho candidate không được hỗ trợ.

Không dùng document-topic prior cho query expansion. Exact alias không bị điều chỉnh.
Đã chạy đúng một lần ngày 15/10/2026. Không thay threshold/trọng số theo validation này
và không mở final-test v4.

## Kết quả k=5

| Phương pháp | Recall@5 | MRR@5 | nDCG@5 |
|---|---:|---:|---:|
| Hybrid | **0,5569** | **0,4035** | **0,4066** |
| Hybrid + document-topic Ontology re-ranking | 0,5580 | 0,4004 | 0,4045 |

Candidate cứu/cải thiện 3 câu, làm xấu 3 câu và làm mất 1 câu khỏi top-5. Recall tăng
0,0011 nhưng MRR giảm 0,0030 và nDCG giảm 0,0022, nên không khái quát kết quả dương
rất nhỏ ở development.

Coverage vẫn là giới hạn: 19/77 query có concept, 25/77 gold evidence có concept nhưng
chỉ 3/77 cặp query-gold có quan hệ Ontology.

## Kiểm định và quyết định

Paired bootstrap 10.000 mẫu cho MRR có CI 95% [-0,0294; +0,0225], p=0,8135;
nDCG có CI [-0,0206; +0,0142], p=0,8373. Không metric nào có ý nghĩa thống kê.

**Không chọn document-topic prior.** Tính năng tiếp tục tắt mặc định; không tuning theo
validation v16 và không chạy lại split này. Nút thắt còn lại là chất lượng/độ phủ quan hệ
query–evidence, không phải thiếu thêm một prior heuristic.
