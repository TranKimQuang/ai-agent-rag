# Supervised concept-linking feasibility (development v18)

## Mục tiêu và giao thức

Kiểm tra liệu 55 câu selection đã audit có đủ để học một concept linker nhẹ hay chưa.
Mỗi câu được dự đoán ngoài fold bằng logistic regression trên sentence embedding:

- 5 fold tách theo paper, gồm 25 paper;
- không có câu nào của paper đánh giá xuất hiện trong tập huấn luyện của fold đó;
- exact alias luôn được giữ làm tín hiệu chắc chắn;
- classifier chỉ được huấn luyện khi fold có ít nhất 2 ví dụ dương cho concept;
- thử các ngưỡng 0,50-0,90;
- không chạy lại 57 câu internal verification.

## Mật độ nhãn

55 câu chỉ có 20 nhãn dương thuộc 9 concept. Bốn concept chỉ có một ví dụ; ba concept
chỉ có hai ví dụ. Chỉ `WordEmbedding` (6) và
`MultilingualNaturalLanguageProcessing` (4) có nhiều hơn hai ví dụ.

## Kết quả

| Phương pháp | Precision | Recall | F1 | Exact match |
|---|---:|---:|---:|---:|
| Alias | 1,000 | 0,600 | 0,750 | 0,855 |
| Supervised + Alias tốt nhất | 1,000 | 0,600 | 0,750 | 0,855 |
| Hybrid 0,55 | **0,933** | **0,700** | **0,800** | **0,873** |

Ở ngưỡng 0,60-0,90, classifier không bổ sung đúng thêm nhãn nào và kết quả bằng Alias.
Ở ngưỡng 0,50, classifier chỉ thêm false positive: Precision giảm còn 0,857, Recall vẫn
0,600 và F1 giảm còn 0,706.

## Kết luận

Không đưa prototype supervised vào pipeline. Kết quả không cho thấy lỗi code mà cho thấy
nút thắt dữ liệu: số ví dụ dương trên từng concept quá ít để học ranh giới ngoài paper.
Hybrid 0,55 tiếp tục là baseline được giữ.

Bước hợp lệ tiếp theo là xác nhận độc lập nhãn hiện tại rồi mở rộng số ví dụ dương cho
các concept mục tiêu. Không nên tiếp tục đổi mô hình trên cùng 55 câu vì sẽ tăng nguy cơ
overfit development.

Artifact máy đọc: `supervised_selection_55_oof.json`.
