# THEO DÕI TIẾN ĐỘ ĐỒ ÁN AI AGENT + RAG

Cập nhật gần nhất: 27/09/2026

### Mới nhất: smoke Agent end-to-end trên QASPER development

- Đã thêm `scripts/smoke_qasper_agent.py` để chạy văn bản QASPER thật qua
  retrieval -> Ontology -> evidence gate -> Qwen3:4b -> citation. Script chặn
  tập held-out và có chế độ retrieval-only để chẩn đoán sáu cấu hình.
- Lần đầu tìm chung 20 paper chỉ có 1/5 câu thấy gold evidence trong top 5;
  Agent vẫn trả lời 4/5 nhưng chỉ 1 câu dẫn gold. Kết quả này phát hiện nguy cơ
  lấy bằng chứng đúng chủ đề nhưng sai paper.
- Đã bổ sung `document_id` tùy chọn cho `/search`, `/ask`, BM25, Semantic,
  Hybrid và Agent. Câu QASPER nay được tìm trong đúng paper của nó; đây là
  ngữ cảnh vốn có của QASPER và cũng cần thiết khi ứng dụng chứa nhiều PDF.
- Chẩn đoán cùng 5 câu cho thấy BM25 hit 3/5, Semantic 2/5, Hybrid 2/5,
  Hybrid + re-ranking 2/5, trong khi hai nhánh có expansion chỉ hit 1/5 ở top 5.
  Query expansion làm câu OpenIE từ hạng 1 rơi khỏi top 5.
- Phát hiện Agent chưa dùng cấu hình đã khóa trong tài liệu: Agent còn gọi cả
  expansion + re-ranking dù development đã chọn re-ranking-only. Đã đồng bộ
  Agent sang `hybrid_ontology_rerank`, không đổi trọng số và không dùng held-out.
- Lần xác nhận cuối trên đúng 5 câu: retrieval hit 2/5; Agent trả lời 3 và từ
  chối 2; 2/3 câu trả lời dẫn đúng gold evidence. Câu còn lại dùng đoạn cùng
  paper nhưng ngoài gold, cho thấy evidence gate còn dễ chấp nhận concept mạnh.
- Log cuối: `results/qasper_agent_smoke_20260926T170515Z.json`. Đây là smoke
  development rất nhỏ, không phải kết quả luận văn hoặc đánh giá answer correctness.
- Toàn bộ 75 test passed; Ruff passed. Còn một cảnh báo deprecation từ
  Starlette/httpx. Bước tiếp theo: hiệu chỉnh evidence gate trên validation và
  mở rộng đánh giá answer/citation trên mẫu QASPER lớn hơn; chưa chạy lại held-out.

### Mới nhất: smoke tiếng Việt và xác nhận GPU

- Qwen3:4b trả lời đúng 3/3 câu có đáp án theo kiểm tra của assistant;
  từ chối 1/1 câu thiếu bằng chứng. Câu so sánh BM25/Semantic dẫn đúng hai nguồn.
- Log: results/local_llm_vi_20260926T162132Z.json. Trung bình 15,650 giây/câu,
  chạy CPU. Đây chỉ là 4 câu dữ liệu tổng hợp, đưa evidence trực tiếp vào LLM;
  chưa phải kiểm thử retrieval/evidence gate end-to-end hay đánh giá QASPER.
- Đã sửa lỗi xuất tiếng Việt trên terminal Windows cp1252 trong script thử.
- Đã cập nhật driver notebook NVIDIA cho GTX 1650 4GB từ 457.34 lên 617.14;
  bộ cài kết thúc thành công và không tự khởi động lại Windows.
- Sau khi khởi động lại Windows, Ollama nhận CUDA 13.4 và GTX 1650 (compute 7.5).
  Vulkan discovery bị watchdog timeout nhưng CUDA hoạt động. Qwen3:4b offload
  26/37 lớp, Ollama báo 67% GPU / 33% CPU và dùng khoảng 2,3 GB VRAM.
- Cold start đầu tiên mất 82,964 giây do GPU discovery, nạp model và tạo cache;
  lượt ngắn tiếp theo khi model đã nóng mất 0,692 giây, đạt 22,51 token/giây.
- Chạy lại 4 câu tiếng Việt trên GPU: 3/3 câu có đáp án đúng nguồn và 1/1 câu
  thiếu bằng chứng được từ chối; thời gian 5,797 / 6,548 / 6,671 / 2,428 giây,
  trung bình 5,361 giây/câu. Log: results/local_llm_vi_20260926T164438Z.json.
- So với đúng smoke CPU trước đó (15,650 giây/câu), lần GPU này nhanh khoảng
  2,92 lần sau khi warm. Đây không phải benchmark tổng quát hay đánh giá QASPER.
- Không thay đổi cấu hình retrieval đã khóa.


### Trạng thái mới nhất: citation bằng ID câu nguồn

- Đã đổi output LLM từ quote tự viết sang sentence_id do server cấp trong
  từng request. Server tự lấy nguyên văn câu và metadata; ID không hợp lệ trả
  lỗi generation (503), không còn giả thành model từ chối vì thiếu evidence.
- Chạy lại 10 câu fixed-evidence: trả lời 7/7 câu có đáp án; từ chối 3/3 câu
  không có đáp án. Hai câu đếm đã trả đúng 20/75. Câu paper còn thừa ý về số câu hỏi.
- Thời gian trung bình 9,862 giây/câu (5,910–13,665 giây), CPU. Không kết luận
  tăng tốc chung từ một lần chạy vì có ảnh hưởng cache và độ dài output.
- 73 test passed; Ruff passed; còn 1 cảnh báo deprecation httpx/Starlette.
- Log mới results/local_llm_sentence_ids_20260926T161317Z.json; giữ nguyên log cũ.
- Đây là kết quả smoke development do assistant kiểm tra, không phải chấm độc
  lập hay benchmark QASPER. ID đúng không chứng minh claim đúng về ngữ nghĩa.
- Chưa bật Ollama mặc định ở API; chọn ANSWER_BACKEND=ollama khi demo.
- Bước kế: câu tiếng Việt, nhiều nguồn, nội dung gây nhiễu và đánh giá end-to-end.
- Các mục bên dưới giữ lịch sử để phân biệt kết quả trước và sau sửa citation.

### Cập nhật 26/09: kiểm tra nguồn của câu trả lời

### Prototype LLM local (26/09)

- Đã thêm OllamaAnswerGenerator, bật bằng ANSWER_BACKEND=ollama; mặc định
  vẫn extractive. Model thử nghiệm dự kiến qwen3:4b, localhost:11434.
- Model trả JSON gồm các claim và quote/chunk_id. Server kiểm tra ID, quote
  nguyên văn và tự lấy metadata nguồn. Đây CHƯA phải kiểm tra entailment.
- Lỗi dịch vụ/JSON/timeout trả 503; từ chối vì evidence trả insufficient_evidence.
- 70 test passed, Ruff passed (1 cảnh báo httpx/Starlette); test LLM dùng mock,
  KHÔNG coi đây là 70 câu hỏi được model thật trả lời đúng.
- Đã có scripts/smoke_local_llm.py: 10 câu synthetic với fixed evidence,
  bao gồm 3 câu unanswerable; chỉ smoke generation, không phải benchmark QASPER.
- Lần chạy trước khi cài runtime thất bại kết nối; sau cài đã chạy đủ 10 câu thật.
- Đã cài Ollama 0.34.4 và tải qwen3:4b (digest đầu 359d7dd4bcda,
  khoảng 2,5 GB). Không cập nhật driver NVIDIA.
- Đã chạy smoke test model thật. Ollama ps xác nhận 100% CPU, context 4096,
  kích thước bộ nhớ model do Ollama báo khoảng 3,2 GB (không phải peak RAM máy).
- Hướng dẫn bật/tắt, chạy thử và giới hạn: LOCAL_LLM.md.
- Kết quả: trả lời 5/7 câu có đáp án, từ chối cả 3 câu không có đáp án.
  Hai câu đếm paper/question bị từ chối dù có evidence; chưa phân biệt model
  từ chối hay quote validator loại vì chưa lưu raw output/rejection reason.
- Thời gian trung bình 14,021 giây/câu, khoảng 3,778–30,708 giây. Assistant
  đọc 5 câu đã trả thấy có nguồn hỗ trợ, nhưng 2 câu thừa ý. Chưa chấm độc lập.
- Báo cáo lần chạy đầu: LOCAL_LLM_SMOKE_REPORT.md. Đây không phải kết quả
  QASPER hoặc đánh giá end-to-end; chưa đo answer/citation precision-recall chính thức.
- Bước kế: bổ sung logging lý do từ chối, kiểm tra 2 câu đếm, rồi thêm câu tiếng
  Việt/nhiều nguồn trước khi chạy end-to-end trên tài liệu thực.

### Chẩn đoán hai câu đếm (26/09)

- Đã chạy scripts/diagnose_local_llm.py, giữ nguyên prompt và validator.
- Model trả đúng 20 paper và 75 question, nhưng cả hai lần tự thêm `2: ` vào
  quote. Bộ kiểm tra nguồn từ chối vì không khớp nguyên văn (quote_not_verbatim).
- Lần chạy lại này không phải model chủ động từ chối. Không có raw output
  lần đầu để khẳng định chính xác chuỗi quote của lần đầu.
- Đã lưu request/response riêng trong results/local_llm_diagnostic_20260926T160840Z.json.
  Script chẩn đoán qua Ruff; không đổi logic ứng dụng hoặc benchmark.
- Hướng sửa đề xuất: model chọn ID câu nguồn, server tự lấy quote nguyên văn;
  vẫn cần kiểm tra nguồn có hỗ trợ claim hay không, không nới lỏng validator.

### Kiểm tra nguồn trích xuất (đã thực hiện trước prototype)

- Agent trích xuất chỉ trả citation của chunk thực sự chứa câu trả lời, thay vì
  tự gắn ba kết quả retrieval đầu tiên. Quote giữ nguyên câu trả lời, không cắt
  phần đầu chunk khiến mất đoạn bằng chứng.
- Câu trả lời rỗng hoặc không khớp nguyên văn evidence bị từ chối.
- Đây là kiểm tra nguồn cho chế độ trích xuất, KHÔNG chứng minh câu trả lời đúng
  về ngữ nghĩa, và chưa phải validator cho câu trả lời diễn đạt lại bằng LLM.
- Chưa gọi LLM thật, chưa chọn provider/model hoặc cấu hình chi phí API.
- Kiểm tra ngày 26/09: 62 test passed, Ruff passed. Còn 1 cảnh báo deprecation
  httpx/Starlette. Lần đầu có 2 lỗi quyền thư mục Temp; chạy lại với basetemp
  riêng trong dự án đã qua toàn bộ test. Không chạy lại benchmark held-out.
- Giữ nguyên benchmark và các held-out đã chạy. Các mốc bên dưới là lịch sử;
  ghi chú “chưa chạy held-out” ở mốc cũ không mô tả trạng thái hiện tại.

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

### Lịch sử thực nghiệm tiếp theo và các hạng mục còn lại

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
- [x] Gán nhãn 30 câu development v3 và bổ sung 21 concept có chọn lọc; Hybrid concept-linking
  F1 tăng từ 0,2703 lên 0,9153 tại threshold 0,65.
- [x] Coverage sau vocabulary v3: query 30/78, gold evidence 47/78 và cặp có quan hệ 18/78.
- [x] Re-ranking sau vocabulary tăng Recall@5 từ 0,2991 lên 0,3120, MRR@5 từ 0,2331
  lên 0,2385 và nDCG@5 từ 0,2306 lên 0,2371; expansion vẫn gây query drift.
- [x] Quét trọng số development v3 và khóa cấu hình: Hybrid linking threshold 0,65,
  re-ranking weight 0,05, không query expansion; held-out v3 chưa chạy.
- [x] Chạy held-out v3 đúng một lần sau commit khóa cấu hình: Hybrid và Ontology re-ranking
  cùng Recall@5 0,2629, MRR@5 0,1448 và nDCG@5 0,1722; không tuning sau test.
- [x] Coverage held-out v3 chỉ đạt query 6/70 và cặp có quan hệ 5/70, xác nhận vocabulary
  theo development chưa khái quát đủ sang các chủ đề paper mới.
- [x] Xây dựng tập dữ liệu thực từ 20 bài QASPER và 75 câu hỏi có gold evidence.
- [x] Chạy ablation đầu tiên trên 42 câu validation và ghi nhận vocabulary ban đầu chỉ
  tạo 22 concept-link, chưa làm thay đổi kết quả Hybrid.
- [x] Mở rộng vocabulary theo validation (không xem test), tăng độ phủ lên 171
  concept-link trên 605 chunk.
- [x] Chạy lại ablation: Ontology re-ranking tăng Recall@5 từ 0,3016 lên 0,3254 và
  MRR@5 từ 0,2381 lên 0,2560; query expansion còn gây query drift nhẹ.
- [ ] Đánh giá độ chính xác của câu trả lời và citation.
- [~] Đã tích hợp adapter và chạy 10 câu với LLM local thật; chưa đánh giá end-to-end.
- [~] AI Agent có nhánh Ollama, evidence gate và kiểm tra quote/ID; chưa đánh giá
  độ đúng ngữ nghĩa của claim/citation.
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

1. Giữ nguyên kết quả held-out v3 và không tiếp tục tuning theo test này.
2. Thiết kế hướng concept linking khái quát hơn (candidate generation từ CSO hoặc zero-shot
   linking), dùng một development protocol mới nếu tiếp tục nghiên cứu retrieval.
3. Song song, tích hợp LLM vào Agent và đánh giá answer correctness/citation/unanswerable.

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
- AI Agent và answer generation: có chế độ trích xuất và adapter Ollama opt-in;
  đã chạy model thật trên CPU với 10 câu đơn giản, chưa chứng minh chất lượng
  sinh câu trả lời trên dữ liệu thực.
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
