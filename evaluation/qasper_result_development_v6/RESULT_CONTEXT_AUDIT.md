# Audit Result extraction trên development v6

## Phạm vi

- Review thủ công toàn bộ 44 instance `Result` trên 20 paper development v6.
- Split này paper-disjoint với 165 paper từng dùng trước đây, bao gồm validation v5.
- Kiểm tra riêng phạm vi `Result` và năm nhóm liên kết: Method, Model, Dataset,
  Metric và Value.

## Kết quả baseline

| Hạng mục | Kết quả |
|---|---:|
| Tổng số instance | 44 |
| Result đúng phạm vi | 30 |
| Non-result | 7 |
| Prior-work | 7 |
| Precision instance Result | 68,18% |

| Role | Đúng / tổng | Precision |
|---|---:|---:|
| Method | 20 / 21 | 95,24% |
| Model | 56 / 57 | 98,25% |
| Dataset | 9 / 16 | 56,25% |
| Metric | 27 / 27 | 100,00% |
| Value | 20 / 20 | 100,00% |

## Nhóm lỗi cần sửa

1. Bảy đoạn method/setup/future-work được tạo thành `Result` dù không báo cáo outcome.
2. Bảy đoạn related work bị gán nhầm thành kết quả của paper hiện tại.
3. Dataset extraction là điểm yếu nhất. Các nhãn chung hoặc sai nguồn như `NLP`,
   `APE`, `Moses BIBREF18`, `parallel corpus` và `Twitter` chiếm 7/16 liên kết.
4. `Faster-RCNN` bị gán Method thay vì Model; từ đầu câu `If` bị nhận thành Model.

## Kết quả hậu sửa trên development

Các quy tắc được sửa chỉ từ development v6: phân biệt setup/prior-work với outcome quan
sát được, nhận diện câu kết quả theo ngữ cảnh, hỗ trợ `acc`, loại nhãn Dataset chung và
chuẩn hóa một số kiến trúc Model.

| Hạng mục | Kết quả |
|---|---:|
| Tổng số instance hậu sửa | 58 |
| Result đúng phạm vi | 57 |
| Prior-work | 1 |
| Precision instance Result | 98,28% |
| Result đúng baseline được giữ lại | 30 / 30 |
| Instance sai baseline còn sót | 0 / 14 |
| Ứng viên mới đã review | 28 |

| Role | Đúng / tổng | Precision |
|---|---:|---:|
| Method | 10 / 10 | 100,00% |
| Model | 56 / 57 | 98,25% |
| Dataset | 7 / 9 | 77,78% |
| Metric | 43 / 43 | 100,00% |
| Value | 47 / 47 | 100,00% |

Số liệu trên không thay thế validation độc lập. Validation v5 không được mở lại để tuning
và final-test v4 vẫn được niêm phong.

## Quy tắc sử dụng

Development v6 được phép dùng để sửa bộ nhận diện `Result` và chuẩn hóa role. Không dùng
validation v5 hoặc final-test v4 để lựa chọn quy tắc. Sau khi sửa và kiểm tra lại trên
development v6, phải khóa code rồi tạo một validation paper-disjoint mới để đánh giá đúng
một lần.

## Artifact

- `result_context_review.json`: nhãn thủ công và quy ước review.
- `result_context_audit.csv`: dữ liệu gốc cùng nhãn theo từng role.
- `result_context_audit_summary.json`: precision tổng hợp.
- `result_context_audit_pending.csv`: snapshot trước review, được giữ nguyên.
- `result_context_review_after_fix.json`: nhãn hậu sửa, gồm review 28 ứng viên mới.
- `result_context_after_fix_summary.json`: số liệu hậu sửa và kiểm tra regression.
