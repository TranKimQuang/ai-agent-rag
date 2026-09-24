# THEO DÕI TIẾN ĐỘ ĐỒ ÁN AI AGENT + RAG

Cập nhật gần nhất: 23/09/2026

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
- [x] Kiểm thử gần nhất: 46 test passed; Ruff không phát hiện lỗi.
- [x] Đồng bộ source code với GitHub.
- [x] Tạo giao diện demo OntoRAG tại trang chủ.
- [x] Tạo API POST /ask và AI Agent phiên bản đầu điều phối retrieval, evidence gate,
  answer generation và kiểm tra citation.
- [x] Thêm cơ chế từ chối trả lời khi evidence không đủ mạnh.
- [x] Kiểm thử tích hợp: câu hỏi về QA/NLP được trả lời kèm trang nguồn; câu hỏi ngoài
  phạm vi về giá vàng bị từ chối.
- [x] Mở rộng Ontology v2 với Paper-Author, Paper-Citation và Paper-Result.
- [x] Mô hình hóa Result liên kết Method/Model-Dataset-Metric-Value và evidence.
- [x] Bổ sung inverse property cùng domain/range cho các quan hệ cấu trúc chính.
- [x] Ánh xạ 5 concept cốt lõi với CSO v3.5 bằng skos:exactMatch và ghi lại nguồn.
- [x] Bổ sung semantic concept linking bằng embedding, giữ alias baseline và chế độ hybrid.
- [x] Thêm API kiểm tra concept linking và benchmark Precision/Recall/F1/Exact Match.
- [x] Thêm skos:definition cho các concept lõi và hiệu chỉnh ngưỡng semantic ban đầu 0,40.
- [x] Chạy benchmark concept-linking mẫu: alias Precision 1,00/Recall 0,50; semantic và
  hybrid Precision 0,462/Recall 1,00. Chỉ dùng để debug, chưa phải kết quả luận văn.
- [x] Tách ablation thành Hybrid, Hybrid + Expansion, Hybrid + Re-ranking và Hybrid + cả hai.
- [x] Chạy ablation trên bộ debug 24 câu: Recall@1 lần lượt 0,458; 0,542; 0,542;
  0,583. Kết quả chỉ kiểm tra pipeline, không dùng làm thực nghiệm chính thức.
- [x] Tải và xác minh QASPER v0.3 chính thức bằng SHA-256.
- [x] Tạo subset QASPER thật: 20 paper, 1.009 paragraph chunk và 75 câu hỏi có evidence;
  chia validation 10 paper/42 câu và test 10 paper/33 câu không trùng paper.
- [x] Chạy ablation trên validation thật: Hybrid và các nhánh Ontology hiện cho cùng kết
  quả; chỉ có 22 concept link/605 chunk, cho thấy vocabulary hiện chưa đủ độ phủ.

### Đang ở trạng thái nền móng

- [~] Ontology đã tồn tại và truy vấn được, nhưng hiện mới là dữ liệu mẫu.
- [x] Ontology đã tham gia mở rộng truy vấn và re-ranking của Hybrid Search.
- [~] Dữ liệu và chỉ mục đang lưu trong RAM, sẽ mất khi khởi động lại server.
- [~] AI Agent đã có prototype điều phối và evidence gate, nhưng tạm dừng mở rộng cho
  tới khi retrieval trên dữ liệu thực ổn định.

### Chưa hoàn thành

- [x] Ánh xạ bước đầu một phần Computer Science Ontology (CSO); sẽ mở rộng có chọn lọc
  khi vocabulary dữ liệu QASPER được xác định.
- [x] Mở rộng liên kết Paper-Author, Paper-Citation và Paper-Result.
- [x] Mô hình hóa Result liên kết Method/Model-Dataset-Metric-Value.
- [x] Bổ sung inverse property, domain/range và các quan hệ suy luận cần thiết.
- [~] Cơ chế gán concept cho chunk đã có; còn cần chạy trên tập PDF thật.
- [x] Gán nhãn thủ công 16 câu QASPER validation để so sánh concept linking; threshold 0,55
  cho Hybrid F1 0,9412, cao hơn Alias F1 0,7143 và Semantic F1 0,7586.
- [x] Đã có công cụ ghi thứ hạng trước/sau cho từng câu; còn cần chạy và chọn ví dụ tốt.
- [x] Tạo tập câu hỏi kiểm soát và gold evidence để đánh giá.
- [x] So sánh BM25, Semantic, Hybrid và Hybrid + Ontology.
- [x] Tính Precision@k, Recall@k, MRR và nDCG@k.
- [x] Tách ablation: Hybrid, +Expansion, +Re-ranking và +Expansion+Re-ranking.
- [x] Quét trọng số Ontology trên validation và chọn 0,10 cho re-ranking; test set chưa chạy.
- [x] Chạy một lần trên 33 câu QASPER test: Semantic tốt nhất trong các baseline hợp lệ.
- [x] Phân tích sau test phát hiện candidate-pool confound ở nhánh Ontology; đã sửa và thêm
  regression test, không tái dùng split này để lựa chọn mô hình.
- [x] Phân tích coverage: 0/33 query có concept, 3/33 gold evidence có concept và không có
  cặp query/evidence nào nhận được quan hệ Ontology.
- [x] Tạo vòng dữ liệu mới từ QASPER train: development 20 bài/72 câu và held-out
  20 bài/72 câu; không trùng paper với các split cũ.
- [x] Đo baseline coverage trên development mới: 1/72 query có concept, 20/72 gold evidence
  có concept và chỉ 1/72 cặp query/evidence có quan hệ Ontology.
- [x] Mở rộng 18 concept theo development: query coverage 20/72, gold coverage 33/72 và
  12/72 cặp query/evidence có quan hệ; held-out vẫn chưa mở.
- [x] Gán nhãn 20 câu development: Hybrid concept linking F1 0,9189 tại threshold 0,60.
- [x] Ablation development mới: Hybrid Recall@5 0,2037; re-ranking giữ Recall và tăng
  MRR@5 từ 0,1648 lên 0,1718; expansion gây query drift.
- [x] Khóa cấu hình v2: re-ranking only, trọng số 0,05, concept threshold 0,60.
- [x] Chạy held-out v2 đúng một lần: Hybrid và các biến thể Ontology bằng nhau vì chỉ
  1/72 query nhận diện được concept; không chỉnh tham số sau held-out.
- [x] Tích hợp Hybrid concept linking (alias + embedding, threshold 0,60) vào ingest,
  query expansion và ontology re-ranking; dùng chung embedding encoder và mã hóa chunk theo lô.
- [x] Chạy lại đúng tập development sau tích hợp semantic linking: Ontology re-ranking tăng
  Recall@5 từ 0,2037 lên 0,2176, MRR@5 từ 0,1648 lên 0,1764 và nDCG@5 từ 0,1576
  lên 0,1697; query expansion tiếp tục gây query drift.
- [x] Tạo protocol v3 hoàn toàn tách biệt: development 20 paper/78 câu và held-out
  20 paper/70 câu; cả 40 paper không trùng nhau và không trùng 60 paper đã dùng trước đó.
- [x] Chạy ablation development v3: Hybrid đạt Recall@5 0,2991 và MRR@5 0,2331;
  Ontology re-ranking không đổi, expansion giảm Recall@5 còn 0,2703.
- [x] Phân tích coverage development v3: 7/78 query có concept, 29/78 gold evidence có
  concept và chỉ 3/78 cặp có quan hệ Ontology; chưa mở held-out v3.
- [x] Sửa pipeline để phân biệt chunk đã index nhưng không có concept, mã hóa chunk theo lô,
  cache embedding câu hỏi và cache kết quả concept linking.
- [x] Xây dựng tập dữ liệu thực từ 20 bài QASPER và 75 câu hỏi có gold evidence.
- [x] Chạy ablation đầu tiên trên 42 câu validation và ghi nhận vocabulary ban đầu chỉ
  tạo 22 concept-link, chưa làm thay đổi kết quả Hybrid.
- [x] Mở rộng vocabulary theo validation (không xem test), tăng độ phủ lên 171
  concept-link trên 605 chunk.
- [x] Chạy lại ablation: Ontology re-ranking tăng Recall@5 từ 0,3016 lên 0,3254 và
  MRR@5 từ 0,2381 lên 0,2560; query expansion còn gây query drift nhẹ.
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

Milestone tiếp theo: kiểm chứng khả năng khái quát của semantic concept linking và hoàn thiện
answer generation.

1. Gán nhãn một tập concept-linking đại diện từ development v3 và phân tích các concept thiếu.
2. Cải thiện semantic concept linking chỉ bằng development v3, rồi khóa cấu hình trong file đã
   commit; chưa mở held-out v3 khi re-ranking chưa tạo tín hiệu ổn định.
3. Sau khi khóa retrieval v3, chỉ chạy held-out một lần rồi tích hợp LLM và đánh giá Agent/citation.

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
- Ontology-aware retrieval: semantic concept linking đã tham gia trực tiếp vào pipeline và
  re-ranking cải thiện development; expansion vẫn gây query drift. Held-out v2 đã được chạy
  đúng một lần trước thay đổi này và không được tái dùng để chọn mô hình.
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
