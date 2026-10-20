# Audit nhãn taxonomy v22

## Quy trình

1. Qwen3:4b review gói mù chỉ với câu hỏi, evidence và catalog taxonomy 22 concept.
2. Mọi concept ngoài catalog bị loại tự động và hạ confidence xuống tối đa 0,5.
3. Rà thủ công toàn bộ 40 câu, đặc biệt mọi nhãn dương và nhãn confidence thấp.
4. Chỉ giữ concept được diễn đạt trực tiếp hoặc là paraphrase rõ trong câu hỏi; evidence
   chỉ dùng để phân giải nghĩa, không được đưa topic mới vào nhãn.

## Kết quả audit

- Reviewer ban đầu: 37 câu dương, 3 câu `NONE` — tỷ lệ dương bất thường.
- Sau audit: 17 câu dương, 23 câu `NONE`, tổng 17 assignment.
- Các lỗi chính: suy topic từ evidence/paper; ép concept ngoài taxonomy sang concept gần
  nhất; nhầm các cụm chung như dataset, metric, representation hoặc feature thành task.
- File full-catalog đầu tiên được giữ với hậu tố `rejected` để kiểm toán và không dùng làm
  nhãn.

## Trạng thái khoa học

Đây là nhãn do LLM độc lập đề xuất rồi được assistant audit, không phải human gold. Có thể
dùng cho development có ghi rõ giới hạn; không dùng như kết quả validation/final chính thức.
