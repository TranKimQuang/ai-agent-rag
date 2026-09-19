# THEO DÕI TIẾN ĐỘ ĐỒ ÁN AI AGENT + RAG

Cập nhật gần nhất: 19/09/2026

## 1. Tên đề tài

Xây dựng hệ thống AI Agent hỗ trợ hỏi đáp tài liệu PDF dựa trên RAG tăng cường Ontology.

## 2. Mục tiêu tổng thể

Hệ thống tiếp nhận tài liệu PDF, tìm các đoạn văn có liên quan, dùng Ontology để mở rộng
truy vấn và xếp hạng lại kết quả, sau đó dùng LLM tạo câu trả lời kèm tên tài liệu, số
trang và đoạn bằng chứng. Nếu tài liệu không có đủ bằng chứng, hệ thống phải từ chối suy
đoán.

## 3. Tiến độ hiện tại

### Đã hoàn thành

- [x] Tạo project Python, virtual environment và Git repository.
- [x] Cấu hình FastAPI và Swagger.
- [x] Đọc nội dung PDF theo từng trang bằng PyMuPDF.
- [x] Chia văn bản thành các chunk có overlap.
- [x] Lưu metadata cơ bản: document_id, chunk_id, filename và page.
- [x] Tìm kiếm từ khóa bằng BM25.
- [x] Tìm kiếm ngữ nghĩa bằng Sentence Transformers.
- [x] Hybrid Search kết hợp BM25 và Semantic bằng RRF.
- [x] Chuẩn hóa tiếng Việt có dấu/không dấu cho BM25.
- [x] API tải PDF: POST /documents.
- [x] API tìm kiếm: GET /search.
- [x] Tạo tài liệu PDF mẫu để kiểm thử.
- [x] Viết các unit test cho PDF, chunking, API và retrieval.
- [x] Tạo Ontology phiên bản đầu trong ontology/document_qa.ttl.
- [x] Tạo các class cơ bản: Paper, Section, Chunk, Concept, ResearchTask, Method, Model,
  Dataset, Metric, Result và Citation.
- [x] Tạo các property cơ bản: hasSection, hasChunk, mentionsConcept, usesMethod,
  usesDataset, evaluatesWithMetric, addressesTask, hasEvidence và relatedConcept.
- [x] Tạo một số instance mẫu: SamplePaper, QASPER, EvidenceF1,
  RetrievalAugmentedGeneration và SampleChunk.
- [x] Viết OntologyService bằng RDFLib để đọc và tra cứu Ontology.
- [x] API thống kê Ontology: GET /ontology/summary.
- [x] API xem quan hệ của concept: GET /ontology/concepts/{concept}.
- [x] Thống nhất tên class/property chính theo góp ý của giảng viên.
- [x] Thêm alias/synonym và quan hệ broader, narrower, relatedTo.
- [x] Tạo file Ontology định dạng RDF/XML: ontology/document_qa.owl.
- [x] Viết 10 competency questions.
- [x] Viết 5 truy vấn SPARQL minh họa.
- [x] Nhận diện concept và alias trong câu hỏi/chunk.
- [x] Mở rộng truy vấn bằng synonym và quan hệ Ontology.
- [x] Tính OntoScore và chạy thử Ontology-aware re-ranking.
- [x] Trả về giải thích concept và lý do tăng hạng trong kết quả tìm kiếm.
- [x] Tự động gán concept vào chunk khi tải PDF.
- [x] Tạo triple Chunk -> mentionsConcept -> Concept trong Knowledge Graph ở RAM.
- [x] Trả về số lượng concept_links sau khi ingest PDF.
- [x] Viết công cụ benchmark bốn phương pháp retrieval.
- [x] Tính tự động Precision@k, Recall@k, MRR và nDCG@k.
- [x] Tạo bộ dữ liệu benchmark mẫu gồm 8 chunk và 10 câu hỏi.
- [x] Xuất kết quả benchmark thành JSON và CSV.
- [x] Mở rộng PDF kiểm thử có kiểm soát lên 16 trang, gồm 8 trang đáp án và 8 trang gây nhiễu gần nghĩa.
- [x] Mở rộng benchmark lên 24 câu hỏi: trực tiếp, đồng nghĩa, gián tiếp, suy luận và Ontology.
- [x] Xuất chỉ số tại k=1, k=3, k=5 và thứ hạng chi tiết của từng câu hỏi.
- [x] Xuất bảng ontology_rank_changes.csv so sánh Hybrid với Hybrid + Ontology.
- [x] Chạy benchmark 24 câu hỏi: Hybrid + Ontology đạt Recall@1 0,583; Recall@3 0,917; Recall@5 0,958.
- [x] Ghi nhận q19 và q24 được Ontology đưa từ ngoài top 5 lên hạng 1.
- [x] Sửa nhãn thay đổi thứ hạng thành rescued, lost và missed_by_both.
- [x] Soạn file Word báo cáo tiến độ gồm kiến trúc, Ontology, SPARQL và kết quả thử nghiệm.
- [x] Kiểm tra PDF qua pipeline thật: trích xuất, chunking, gán concept và BM25.
- [x] Kiểm thử gần nhất: 32 test passed; Ruff không phát hiện lỗi.
- [x] Đồng bộ source code với GitHub.
- [x] Tạo giao diện demo OntoRAG tại trang chủ.
- [x] Tạo API POST /ask và AI Agent phiên bản đầu điều phối retrieval, evidence gate,
  answer generation và kiểm tra citation.
- [x] Thêm cơ chế từ chối trả lời khi evidence không đủ mạnh.
- [x] Kiểm thử tích hợp: câu hỏi về QA/NLP được trả lời kèm trang nguồn; câu hỏi ngoài
  phạm vi về giá vàng bị từ chối.

### Đang ở trạng thái nền móng

- [~] Ontology đã tồn tại và truy vấn được, nhưng hiện mới là dữ liệu mẫu.
- [x] Ontology đã tham gia mở rộng truy vấn và re-ranking của Hybrid Search.
- [~] Dữ liệu và chỉ mục đang lưu trong RAM, sẽ mất khi khởi động lại server.
- [~] AI Agent đã có prototype điều phối và evidence gate, nhưng tạm dừng mở rộng cho
  tới khi retrieval trên dữ liệu thực ổn định.

### Chưa hoàn thành

- [ ] Tìm hiểu và ánh xạ một phần Computer Science Ontology (CSO).
- [ ] Mở rộng liên kết Paper-Author, Paper-Citation và Paper-Result.
- [ ] Mô hình hóa Result liên kết Method/Model-Dataset-Metric-Value.
- [ ] Bổ sung inverse property, domain/range và các quan hệ suy luận cần thiết.
- [~] Cơ chế gán concept cho chunk đã có; còn cần chạy trên tập PDF thật.
- [ ] Thử semantic concept linking bằng embedding và so sánh với alias-based linking.
- [x] Đã có công cụ ghi thứ hạng trước/sau cho từng câu; còn cần chạy và chọn ví dụ tốt.
- [x] Tạo tập câu hỏi kiểm soát và gold evidence để đánh giá.
- [x] So sánh BM25, Semantic, Hybrid và Hybrid + Ontology.
- [x] Tính Precision@k, Recall@k, MRR và nDCG@k.
- [ ] Tách ablation: Hybrid, +Expansion, +Re-ranking và +Expansion+Re-ranking.
- [ ] Chọn trọng số Ontology trên validation set, chỉ đánh giá cuối trên test set.
- [ ] Xây dựng tập dữ liệu thực từ 20-30 bài QASPER và tối thiểu 50-100 câu hỏi.
- [ ] Đánh giá độ chính xác của câu trả lời và citation.
- [ ] Tích hợp LLM để tạo câu trả lời dựa trên evidence.
- [~] Đã có AI Agent điều phối retrieval, Ontology, evidence và citation; chưa tích hợp LLM.
- [x] Thêm cơ chế từ chối khi không đủ evidence.
- [x] Tạo giao diện demo.
- [ ] Chuyển sang PostgreSQL + pgvector sau khi pipeline Ontology chạy đúng.

## 4. Pipeline mục tiêu

PDF
-> Chunk
-> Nhận diện/Gán Concept
-> Ontology/Knowledge Graph
-> Query Expansion
-> BM25 + Semantic Retrieval
-> RRF
-> Ontology-aware Re-ranking
-> LLM tạo câu trả lời
-> Citation và Explanation

## 5. Bước tiếp theo ưu tiên

Milestone tiếp theo: Ontology v2 và thực nghiệm retrieval trên dữ liệu thật.

1. Mở rộng mô hình Author, Citation và Result cùng inverse property/domain/range.
2. Ánh xạ nhánh IR/NLP/QA/RAG/Semantic Search với một phần CSO.
3. Bổ sung semantic concept linking và đánh giá so với alias-based baseline.
4. Tách bốn cấu hình ablation của Ontology và chọn trọng số bằng validation set.
5. Chuẩn bị 20-30 bài QASPER cùng 50-100 câu hỏi/evidence thật để đánh giá.
6. Chỉ sau khi retrieval ổn định mới tiếp tục tích hợp LLM và hoàn thiện Agent.

Chưa ưu tiên trong milestone này: mở rộng giao diện, PostgreSQL, pgvector, OCR và
framework Agent phức tạp.

## 6. Nội dung cần có trong lần báo cáo tiếp theo

- [x] File Word báo cáo tiến độ.
- [x] Sơ đồ kiến trúc hệ thống hoàn chỉnh.
- [x] Sơ đồ Ontology và danh sách class/property.
- [x] 5-10 competency questions.
- [x] Instance mẫu tạo từ tài liệu.
- [x] 3-5 câu SPARQL minh họa.
- [x] Có ví dụ q19, q22 và q24 cho thấy Ontology thay đổi thứ hạng.
- [x] Bảng kết quả BM25, Semantic, Hybrid và Hybrid + Ontology tại k=1, 3, 5.
- [x] File ontology .owl và .ttl.
- [x] Source code và GitHub repository.

## 7. Đánh giá tổng quan

- Nền tảng RAG cơ bản: đã hoàn thành.
- Hybrid Search: đã hoàn thành.
- Ontology nền tảng: đã hoàn thành.
- Ontology-aware retrieval: đã có kết quả kiểm soát ban đầu, chưa đánh giá trên PDF khoa học thực tế.
- AI Agent và answer generation: đã có prototype an toàn dùng câu trích xuất; chưa gọi LLM.
- Mức độ hoàn thành ước lượng của toàn đồ án: khoảng 60%.
- Đã đủ cho báo cáo tiến độ về Ontology-aware retrieval; chưa phải kết quả thực nghiệm cuối cùng.
- Bộ PDF 16 trang/24 câu chỉ dùng để debug pipeline, không dùng làm kết quả chính thức.

## 8. Lệnh kiểm tra nhanh

Mở Terminal tại thư mục project và chạy:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pytest -q
python -m ruff check .
python -m uvicorn app.main:app --reload
```

Mở Swagger tại: http://127.0.0.1:8000/docs

GitHub: https://github.com/TranKimQuang/ai-agent-rag

## 9. Quy tắc cập nhật file này

Mỗi khi hoàn thành một phần:

1. Đổi `[ ]` thành `[x]` cho công việc đã hoàn thành.
2. Ghi lại kết quả test mới nhất.
3. Cập nhật ngày ở đầu file.
4. Ghi rõ milestone đang làm và bước tiếp theo.
5. Commit và push file cùng source code lên GitHub.
