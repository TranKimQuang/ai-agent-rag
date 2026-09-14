# THEO DÕI TIẾN ĐỘ ĐỒ ÁN AI AGENT + RAG

Cập nhật gần nhất: 14/09/2026

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
- [x] Tạo PDF kiểm thử có kiểm soát gồm 8 trang và 8 chủ đề.
- [x] Tạo 12 câu hỏi có gold chunk tương ứng từ PDF kiểm thử.
- [x] Kiểm tra PDF qua pipeline thật: trích xuất, chunking, gán concept và BM25.
- [x] Kiểm thử gần nhất: 29 test passed; Ruff không phát hiện lỗi.
- [x] Đồng bộ source code với GitHub.

### Đang ở trạng thái nền móng

- [~] Ontology đã tồn tại và truy vấn được, nhưng hiện mới là dữ liệu mẫu.
- [~] Ontology và Hybrid Search vẫn là hai khối riêng, chưa ảnh hưởng lẫn nhau.
- [~] Dữ liệu và chỉ mục đang lưu trong RAM, sẽ mất khi khởi động lại server.

### Chưa hoàn thành

- [ ] Tìm hiểu và ánh xạ một phần Computer Science Ontology (CSO).
- [~] Cơ chế gán concept cho chunk đã có; còn cần chạy trên tập PDF thật.
- [ ] Ghi log thứ hạng trước/sau để tạo ví dụ báo cáo từ dữ liệu thật.
- [ ] Tạo tập câu hỏi và gold evidence để đánh giá.
- [ ] So sánh BM25, Semantic, Hybrid và Hybrid + Ontology.
- [ ] Tính Precision@k, Recall@k, MRR hoặc nDCG@k.
- [ ] Đánh giá độ chính xác của câu trả lời và citation.
- [ ] Tích hợp LLM để tạo câu trả lời dựa trên evidence.
- [ ] Xây dựng AI Agent điều phối retrieval, Ontology và LLM.
- [ ] Thêm cơ chế từ chối khi không đủ evidence.
- [ ] Tạo giao diện demo.
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

Milestone tiếp theo: Hoàn thành Ontology-aware retrieval trên dữ liệu nhỏ.

1. Chọn một tập PDF thật nhỏ và xác định vocabulary phù hợp.
2. Kiểm tra thủ công độ chính xác của các concept được gán.
3. Tạo 10-20 câu hỏi thử nghiệm có đáp án/chunk đúng từ PDF thật.
4. Chạy và lập bảng so sánh bốn phương pháp retrieval.
5. Tạo ví dụ thật cho thấy Ontology làm thay đổi thứ hạng chunk.

Chưa ưu tiên trong milestone này: giao diện đẹp, PostgreSQL, pgvector và OCR.

## 6. Nội dung cần có trong lần báo cáo tiếp theo

- [ ] File Word báo cáo tiến độ.
- [ ] Sơ đồ kiến trúc hệ thống hoàn chỉnh.
- [ ] Sơ đồ Ontology và danh sách class/property.
- [x] 5-10 competency questions.
- [ ] Instance mẫu tạo từ tài liệu.
- [x] 3-5 câu SPARQL minh họa.
- [~] Đã có ví dụ tự động trong test; còn thiếu ví dụ trên PDF thật.
- [ ] Bảng kết quả BM25, Semantic, Hybrid và Hybrid + Ontology.
- [x] File ontology .owl và .ttl.
- [x] Source code và GitHub repository.

## 7. Đánh giá tổng quan

- Nền tảng RAG cơ bản: đã hoàn thành.
- Hybrid Search: đã hoàn thành.
- Ontology nền tảng: đã hoàn thành.
- Ontology-aware retrieval: đã có bản thử nghiệm, chưa đánh giá trên PDF thật.
- AI Agent và answer generation: chưa hoàn thành.
- Mức độ hoàn thành ước lượng của toàn đồ án: khoảng 40%.
- Chưa đủ cho gói báo cáo chính thức lần tiếp theo; cần hoàn thành milestone
  Ontology-aware retrieval và bảng đánh giá ban đầu.

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
