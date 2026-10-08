# Audit Result-context trên validation v5

## Phạm vi

- Review độc lập toàn bộ 29 instance `Result` được trích từ 20 paper validation v5.
- Review sau khi đã khóa weight `0,20`; không dùng nhãn audit để thay đổi cấu hình hoặc
  chạy lại validation.
- Mỗi dòng được kiểm tra cả phạm vi `Result` và năm nhóm liên kết: Method, Model,
  Dataset, Metric và Value.

## Kết quả

| Hạng mục | Kết quả |
|---|---:|
| Tổng số instance | 29 |
| Result đúng phạm vi | 15 |
| Non-result | 14 |
| Precision instance Result | 51,72% |

| Role | Đúng / tổng | Precision |
|---|---:|---:|
| Method | 6 / 8 | 75,00% |
| Model | 26 / 29 | 89,66% |
| Dataset | 13 / 15 | 86,67% |
| Metric | 27 / 27 | 100,00% |
| Value | 6 / 8 | 75,00% |

## Lỗi chính

1. Bộ trích xuất vẫn coi phần thiết lập thí nghiệm, cấu hình mô hình, định nghĩa metric
   hoặc mô tả phương pháp là một `Result`, dù đoạn văn không báo cáo kết quả quan sát.
2. Một số nhãn chưa được chuẩn hóa: `INLINEFORM0`, `For DPCNN` và
   `PARADISE BIBREF3` giữ lại placeholder/cụm thừa.
3. Một số loại thực thể bị nhầm vai trò: `AV` là task/category nhưng được gán Method;
   `BLEU` là metric nhưng được gán Model; `Dutch` là ngôn ngữ nhưng được gán Dataset.
4. Giá trị `0.5` trong định nghĩa `50p-Acc` bị hiểu nhầm là điểm kết quả ở hai đoạn.

## Kết luận sử dụng

Result-context scoring vẫn cải thiện retrieval trên validation, nhưng precision trích xuất
instance mới chỉ đạt 51,72% trên paper chưa quan sát. Vì vậy chưa nên chạy final-test v4.
Bước phù hợp tiếp theo là tạo một development split paper-disjoint mới để sửa bộ nhận diện
`Result` theo ngữ cảnh; validation v5 và cấu hình đã khóa phải được giữ nguyên làm bằng
chứng đánh giá, không dùng lại để tuning.

## Artifact

- `result_context_review.json`: nhãn thủ công và quy ước review có thể tái tạo.
- `result_context_audit.csv`: toàn bộ dữ liệu gốc, nhãn từng role và ghi chú từng dòng.
- `result_context_audit_summary.json`: số liệu precision tổng hợp.
- `result_context_audit_pending.csv`: snapshot trước review, được giữ nguyên.
