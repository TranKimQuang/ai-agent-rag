# THEO DÕI TIẾN ĐỘ ĐỒ ÁN AI AGENT + RAG

Cập nhật gần nhất: 07/10/2026

### Mới nhất: Audit và sửa precision cho Result-centric scoring v2

- [x] Review thủ công toàn bộ 52 Result development ban đầu; lưu nhãn tái tạo được theo
  từng role trong `result_context_review.json`, không dùng final-test.
- [x] Audit ban đầu: 32 Result đúng phạm vi, 15 non-result, 4 prior-work và 1 mơ hồ;
  precision Result 62,75% khi bỏ dòng mơ hồ.
- [x] Siết bộ lọc section/scope, chỉ nhận metric value trong cùng câu có metric, bổ sung
  AUC/ERR/H@k và sửa phân loại kiến trúc BLSTM/LSTM/CNN/RNN/BERT/GPT/Transformer/LR.
- [x] Hậu sửa còn 39 Result: 38 đúng phạm vi, 1 mơ hồ và 0 dòng đã xác nhận sai.
  Precision role: Method 100%, Model 100%, Dataset 94,44%, Metric 100%, Value 100%.
- [x] Benchmark development 74 câu hậu sửa tại weight 0,30: Recall@5 0,3027 -> 0,3297,
  MRR@5 0,2074 -> 0,2182 và nDCG@5 0,2113 -> 0,2302; 2 câu được cứu vào top 5,
  không mất câu nào.
- [x] Giữ snapshot trước/hậu sửa và báo cáo tại `evaluation/qasper_protocol_v4/`.
- [ ] Chưa chạy validation/final-test. Bước kế tiếp là tạo validation mới từ paper chưa
  từng quan sát để kiểm tra khả năng khái quát, vì precision hậu sửa hiện vẫn đo trên
  development đã dùng để thiết kế quy tắc.
- [x] Đã chuẩn bị validation v5 độc lập gồm 20 paper, 1.109 chunk và 75 câu hỏi; loại
  145 paper từ toàn bộ chín split cũ, overlap bằng 0. Trạng thái hiện là
  `prepared_not_evaluated`; final-test v4 vẫn sealed.
- [ ] Cần khóa/commit code và weight candidates trước khi chạy validation v5 đúng một lần.

### Result-centric knowledge graph và relation scoring v2 (trước audit)

- [x] Khi ingest, mỗi chunk có bằng chứng thực nghiệm phù hợp được mô hình hóa thành
  `Paper -> hasResult -> Result -> hasEvidence -> Chunk` thay vì chỉ gắn concept rời rạc.
- [x] Result liên kết có phạm vi theo đúng paper/chunk với `resultUsesMethod`,
  `resultUsesModel`, `resultUsesDataset`, `measuredBy` và `metricValue`.
- [x] Không thêm vocabulary toàn cục. Tên Model/Dataset/Metric chưa có trong Ontology được
  tạo thành paper-scoped entity, chỉ dùng trong paper tương ứng và không tham gia query expansion.
- [x] Thêm bộ lọc các nhãn chung/false positive như `The model`, `This model`,
  `Neural model`; giữ các tên cụ thể như `BLSTM-CNN-CRF`, `MultiWOZ`, `BLEU`.
- [x] Trên development 1.019 chunk, tạo 52 Result với 21 Method, 56 Model,
  20 Dataset, 49 Metric và 20 Value links sau lọc.
- [x] Development 74 câu tại weight 0,30: Recall@5 tăng 0,3027 -> 0,3162,
  MRR@5 0,2074 -> 0,2137 và nDCG@5 0,2113 -> 0,2235; 2 câu tốt hơn,
  1 câu được cứu vào top 5, 1 câu xấu đi và không mất câu nào khỏi top 5.
- [x] Công cụ benchmark nhận `--ontology-weight` để xuất đầy đủ rank changes cho cấu hình
  Result-centric đã chọn trên development.
- [x] Lưu artifact tại `evaluation/qasper_protocol_v4/result_context_development.json`,
  `result_context_development_weight_030/` và `RESULT_CONTEXT_REPORT.md`.
- [x] Xuất 52 dòng Result kèm text, role và cột review tại
  `evaluation/qasper_protocol_v4/result_context_audit.csv`; bộ lọc tự động không còn nhãn
  model chung đã biết, nhưng toàn bộ dòng vẫn để `pending` để không giả lập đánh giá thủ công.
- [x] Audit thủ công paper-scoped entity đã hoàn thành; validation/final-test chưa chạy.

### Mới nhất: Context-aware Ontology scoring v1

- [x] Không thêm vocabulary mới; thay điểm relation cố định bằng điểm có xét loại thực thể
  câu hỏi yêu cầu, explicit mention trong query/passage và độ đặc hiệu của concept trong graph.
- [x] Đổi phép hợp nhất từ nội suy độc lập sang bonus nhân theo điểm RRF đã chuẩn hóa. Nhờ đó
  passage retrieval yếu không thể vượt lên chỉ vì chứa một concept rộng.
- [x] Thêm kiểm thử cho type intent, explicit/semantic-only evidence và tích hợp re-ranking.
- [x] Trên development 74 câu, weight 0,10 giữ Recall@5 0,3027, tăng MRR@5
  0,2074 -> 0,2200 và nDCG@5 0,2113 -> 0,2211; 2 câu tốt hơn, không có câu xấu đi.
- [x] Weight 0,40 đạt nDCG@5 0,2202 và Recall@5 0,3054 nhưng có 1 câu xấu đi, nên không
  chọn chỉ dựa trên development.
- [x] Trên validation 35 câu, toàn bộ weight 0,00-1,00 đều hòa Hybrid và không đổi hạng.
  Vì vậy tiếp tục chọn Hybrid/weight 0,0; final-test vẫn `sealed_not_evaluated`.
- [x] Lưu đầy đủ kết quả và quyết định tại
  `evaluation/qasper_protocol_v4/CONTEXT_SCORING_REPORT.md`,
  `context_scoring_development.json` và `context_scoring_validation.json`.
- [ ] Bước nghiên cứu tiếp theo: mô hình hóa quan hệ theo từng paper/result và học calibration
  trên một validation mới độc lập; không xem lại final-test hiện tại.

### Mới nhất: đánh giá hình thức Ontology bằng reasoner và competency questions

- [x] Tích hợp OWL-RL reasoner (`owlrl`) và tạo công cụ đánh giá có thể chạy lại bằng
  `python scripts/evaluate_ontology.py`.
- [x] Kiểm tra consistency: 575 triple ban đầu, 1.670 triple sau suy luận,
  1.095 triple suy ra và không phát hiện mâu thuẫn theo các kiểm tra OWL-RL hỗ trợ.
- [x] Hoàn thiện đủ 10 truy vấn SPARQL cho 10 competency questions; toàn bộ 10/10
  đạt số dòng kết quả tối thiểu trên các instance mẫu.
- [x] Xuất artifact đối chiếu tại `evaluation/ontology_quality_report.json` và
  `evaluation/ONTOLOGY_QUALITY_REPORT.md`.
- [x] Báo cáo thống kê 14 class, 25 object property, 10 datatype property,
  76 individual, 35/35 property có domain/range và 8 object property có inverse.
- [x] Rà soát 8 ánh xạ CSO 3.5: giữ 2 `skos:exactMatch` cho Information Retrieval/NLP,
  đổi Question Answering/RAG/Semantic Search sang 3 `skos:closeMatch` do khác vai trò
  mô hình cục bộ; thêm 3 `exactMatch` candidate có kiểm soát và sửa URI RAG sang
  `retrieval-augmented_generation`.
- [x] Chạy paired bootstrap 10.000 mẫu trên 78 câu development cho Hybrid so với
  Ontology re-ranking. Chênh lệch Recall@5 +0,0128 có CI 95%
  [-0,0256; 0,0641], MRR@5 +0,0053 có CI [-0,0045; 0,0162] và nDCG@5
  +0,0066 có CI [-0,0099; 0,0254]; tất cả đều chưa có ý nghĩa ở mức 0,05.
- [x] Lưu kết quả significance tại
  `evaluation/qasper_train_v3/development_significance.json` và
  `evaluation/qasper_train_v3/DEVELOPMENT_SIGNIFICANCE.md`.
- [x] Toàn bộ 125 test và Ruff đạt trên mã nguồn chính (`app`, `scripts`, `tests`).

### Protocol v4: development/validation/final-test mới

- [x] Tải lại QASPER train chính thức và xác minh SHA-256
  `9af08092ee26c4f700202c1f90d1592b662926f23f3a308a10ff0a53345e37fe`.
- [x] Loại 100 paper đã xuất hiện trong sáu split cũ và chia theo seed `20261003`:
  development 20 paper/74 câu, validation 10 paper/35 câu và final-test 15 paper/57 câu.
- [x] Ba split không trùng paper; manifest lưu SHA-256 cho từng file. Final-test được đánh dấu
  `sealed_not_evaluated` và chưa chạy retrieval.
- [x] Baseline development v4: Semantic tốt nhất với Recall@5 0,3270; Hybrid đạt 0,3027;
  Ontology re-ranking giữ nguyên Recall và chỉ tăng MRR@5 từ 0,2074 lên 0,2092.
- [x] Coverage development v4 còn thấp: 9/74 query có concept, 34/74 gold evidence có
  concept và chỉ 5/74 cặp query/evidence có quan hệ Ontology.
- [x] Paired bootstrap 10.000 mẫu trên development v4: Recall không đổi; MRR tăng 0,0018
  nhưng chỉ một câu thay đổi và chưa có ý nghĩa thống kê (`p=0,7489`).
- [x] Phân tích đủ 65 query chưa có concept trên development bằng top-5 semantic
  candidates: 3 câu gần ngưỡng 0,65; 27 câu có weak match và 35 câu thuộc nhóm
  vocabulary gap/câu hỏi chung. Kết quả cho thấy không nên hạ ngưỡng đồng loạt.
- [x] Loại `SampleRAGModel` (instance minh họa) khỏi vocabulary có thể link; chạy lại
  development baseline cho kết quả không đổi, xác nhận lỗi này chưa làm sai các chỉ số đã báo.
- [x] Xuất hàng đợi review tại
  `evaluation/qasper_protocol_v4/development_concept_review.csv` cùng báo cáo JSON/Markdown.
- [x] Thêm thí nghiệm query type-intent cho `Model`, `Dataset`, `Metric`, `Method`, `Task`
  dưới cờ mặc định tắt. Coverage query tăng 9/74 -> 42/74 và số cặp query/evidence
  có quan hệ tăng 5/74 -> 18/74.
- [x] Type-intent re-ranking giữ Recall@5 0,3027 và tăng MRR@5 0,2074 -> 0,2110,
  nhưng chỉ cải thiện 2/74 câu và chưa có ý nghĩa (`p=0,2704`). Query expansion giảm
  Recall@5 còn 0,2757, nên chưa bật cấu hình này làm mặc định.
- [x] Bổ sung candidate generation từ nguồn vocabulary ngoài cho 32 query còn thiếu;
  sau khi ổn định mới dùng validation để chọn cấu hình.
- [x] Tải CSO 3.5 chính thức (SHA-256 `f8dda279...f61d6b`), đọc 138.419 triple/
  14.636 topic và lấy 1.901 topic thuộc sáu nhánh AI/NLP/IR/QA/Semantic Search/ML.
- [x] Sinh top-5 CSO candidates cho 32 query còn thiếu: 15 câu có top score >= 0,60,
  nhưng bộ lọc semantic + lexical bảo thủ chỉ giữ 3 candidate để tránh false positive.
- [x] Thêm mapping `HumanEvaluation`, `TargetLanguage`, `MachineTranslation`; khi kích hoạt,
  coverage tăng 42/74 -> 45/74 và concept link 370 -> 406 nhưng MRR@5 giảm
  0,2110 -> 0,2088. Vì vậy giữ mapping trong Ontology nhưng đặt `retrievalEnabled=false`.
- [x] Chạy validation 35 câu cho type-intent bật/tắt và weight 0,0–0,20. Mọi cấu hình
  re-ranking tốt nhất đều hòa Hybrid tại weight 0,0; expansion không cải thiện.
  Khóa lựa chọn validation là Hybrid thuần và tiếp tục niêm phong final-test.
- [x] Đã triển khai Context-aware Ontology scoring v1; validation chưa cải thiện nên chưa
  bật re-ranking và chưa chạy final-test.

### Trước đó: phân tích lỗi và thử mở rộng evidence cho LLM

- Phân loại 52 case development cho thấy nút thắt chính vẫn là retrieval/context:
  22 retrieval miss, 6 câu có gold evidence ở hạng 4-5 nhưng LLM chỉ nhận top 3,
  3 gate false rejection, 10 lỗi nội dung/định dạng và 1 lỗi chọn citation.
- Thử cross-encoder trên đủ 50 câu answerable: Recall@5 tăng 0,560 -> 0,660,
  MRR tăng 0,342 -> 0,515; candidate Recall@20 là 0,860. Đây vẫn là kết quả
  development và chưa đủ để đổi retrieval mặc định.
- Agent nay cho phép cấu hình số chunk gửi sang bộ sinh từ 1 đến 5; mặc định
  vẫn là 3. Citation validator chỉ chấp nhận ID thuộc đúng số chunk được gửi.
- Trên 6 lỗi context-cutoff đã biết, 5 chunk tăng Answer-F1 0,302 -> 0,600 và
  Evidence-F1 0,000 -> 0,639. Đây là tập lỗi được chọn trước nên không dùng làm
  kết quả tổng quát.
- Đối chứng đủ cùng 50 câu answerable: 5 chunk tăng Answer-F1 0,314 -> 0,366,
  Evidence-F1 0,307 -> 0,373, citation precision/recall 0,317/0,290 ->
  0,370/0,387; số câu được trả lời giữ nguyên 40/50, không có generation error.
- Đổi lại, strict unanswerable bị từ chối đúng giảm từ 2/2 xuống 1/2 và thời
  gian trung bình tăng 10,077 -> 14,015 giây/câu. Vì an toàn quan trọng hơn,
  chưa đổi mặc định sang 5 chunk; đây chỉ là tùy chọn thí nghiệm.
- Báo cáo: `QASPER_ANSWER_EVALUATION.md`; artifacts cục bộ:
  `results/qasper_answer_error_analysis_50.json`,
  `results/qasper_cross_encoder_reranker_50.json` và
  `results/qasper_answer_evaluation_20260929T032301Z.json`.
- 103 test passed; Ruff passed; còn một cảnh báo deprecation Starlette/httpx.
- Bước kế tiếp: thêm bước kiểm tra claim có thực sự được evidence hỗ trợ hoặc
  context thích ứng, rồi đánh giá với nhiều câu unanswerable hơn; chưa chạy
  held-out cuối.

### Prototype kiểm tra answer có được citation hỗ trợ

- Đã thêm `OllamaAnswerSupportVerifier`: sau khi server xác minh sentence ID và
  quote, một lượt LLM local riêng kiểm tra answer có trả lời đúng câu hỏi và có
  được các quote hỗ trợ trực tiếp hay chỉ cùng chủ đề.
- Verifier đã chặn đúng ca unanswerable mà chế độ 5 chunk từng trả lời nhầm:
  nguồn nói về vấn đề đánh giá word embedding, không phải nhược điểm của word
  embedding được đề xuất.
- Pilot cuối trên 4 ca answerable đã biết: giữ 2 answer có nguồn trực tiếp; chặn
  1 answer thêm chữ `F1 score` khi citation chỉ ghi `micro-averaged`; chặn 1
  danh sách collection không thực sự là NLP task. Đây là hành vi an toàn hợp lý,
  nhưng chưa phải điểm benchmark vì mẫu được chọn từ lỗi đã biết.
- Đã sửa công cụ evaluation để chạy ổn khi chọn riêng toàn câu answerable hoặc
  toàn câu unanswerable; trước đó phép tính trung bình nhóm rỗng bị lỗi.
- Có thể bật bằng `ANSWER_SUPPORT_CHECK=ollama` trong API hoặc
  `--verify-answer-support` trong evaluation. Mặc định vẫn tắt vì cần thêm một
  lượt gọi Qwen3:4b, độ trễ cao và chưa đánh giá đủ false rejection.
- 107 test passed; Ruff passed; còn một cảnh báo deprecation Starlette/httpx.
- Bước kế tiếp: tạo tập nhãn supported/unsupported lớn hơn để đo precision,
  recall và chọn ngưỡng/chính sách trước khi cân nhắc bật verifier mặc định.

### Mới nhất: mở rộng đánh giá Agent lên 50 câu answerable QASPER thật

- Đã chạy toàn luồng document-scoped Hybrid + Ontology re-ranking -> evidence
  gate -> Qwen3:4b -> citation trên 50 câu answerable từ 20 paper development.
- Có thêm 2 câu strict natural unanswerable (toàn bộ annotator đều ghi
  Unanswerable); trong 20 paper đã chọn không có đủ 5 câu loại này.
- Trên 50 câu answerable: Answer-F1 0,314; Evidence-F1 0,307; citation
  precision/recall 0,317/0,290; Agent trả lời 40/50 câu.
- Agent từ chối đúng 2/2 câu unanswerable; không có generation error; thời gian
  trung bình toàn bộ 52 case là 10,077 giây/câu.
- Đã thêm retry tối đa 2 lần cho output Ollama lỗi tạm thời. Output hợp lệ
  `insufficient_evidence` không bị retry hoặc biến thành câu trả lời giả.
- Semantic diagnostic trên 50 câu: similarity trung bình 0,517, tương quan với
  token F1 là 0,839; xuất 26 ca cần review thủ công.
- Đã tiền kiểm 26 ca bằng nhãn đề xuất tách riêng: 10 đúng, 8 đúng một phần,
  8 sai; 22/26 citation hỗ trợ claim được sinh. Đây là gợi ý do AI tạo, không
  được báo cáo như human evaluation trước khi người thực xác nhận.
- Phiếu CSV giữ nguyên các cột `manual_*` trống để người chấm xác nhận hoặc sửa;
  nguồn gợi ý có giải thích được lưu tại
  `evaluation/qasper_answer_review_suggestions.json`.
- Điểm thấp hơn mẫu 20 câu là do mẫu mở rộng khó và đa dạng hơn, không phải lỗi
  chạy. Kết quả vẫn là development; chưa tải hoặc chạy held-out cuối.
- Artifacts cục bộ: `results/qasper_answer_evaluation_20260928T085754Z.json`,
  `results/qasper_answer_semantic_review_50.json` và
  `results/qasper_answer_manual_review_50.csv`.
- 99 test passed; Ruff passed; còn một cảnh báo deprecation Starlette/httpx.
- Bước kế tiếp: người dùng xác nhận/sửa nhãn 26 ca, khóa cấu hình, rồi mới chạy
  held-out đúng một lần để tránh tuning theo test.

### Mới nhất: semantic diagnostic và phiếu review thủ công

- Đã thêm `scripts/evaluate_answer_semantics.py` để tính semantic similarity
  giữa prediction và gold answer, đồng thời xuất CSV cho người đánh giá.
- Trên 20 câu answerable development: mean Answer-F1 0,433; mean semantic
  similarity 0,596; tương quan Pearson 0,839.
- Công cụ đánh dấu 10/20 câu cần review, trong đó 2 câu có F1 < 0,50 nhưng
  semantic similarity >= 0,70; đây là các ca token overlap có thể đánh giá thấp
  câu diễn đạt đúng ý.
- CSV tách riêng manual answer correctness (0/1/2), citation support (0/1) và
  ghi chú; semantic similarity chỉ là proxy, không được gọi là factual accuracy.
- Rà soát ban đầu xác nhận citation đúng với claim chưa đảm bảo claim trả lời
  đúng trọng tâm; trường hợp PAN 2017 là ví dụ rõ.
- Báo cáo: `ANSWER_SEMANTIC_REVIEW.md`; artifacts cục bộ trong `results/`.
- 97 test passed; Ruff passed; còn một cảnh báo deprecation Starlette/httpx.
- Bước kế tiếp: người đánh giá điền nhãn thủ công trên mẫu lớn hơn, sau đó báo
  cáo answer correctness và citation support tách biệt với token/evidence F1.

### Mới nhất: định dạng câu trả lời theo loại câu hỏi

- Đã thêm phân loại tất định từ chính câu hỏi: `boolean`, `number`,
  `short_phrase_or_list`, `explanation`; không dùng nhãn gold hoặc nội dung
  held-out.
- Chỉ câu boolean được phép bắt đầu Yes/No; câu số trả giá trị + đơn vị trước;
  câu what/which/who trả cụm ngắn hoặc danh sách; câu how dùng một câu giải thích.
- Đối chứng đủ 22 câu development với retrieval/gate mặc định không đổi:
  Answer-F1 answerable tăng 0,349 -> 0,433; số câu trả lời tăng 16 -> 17;
  vẫn từ chối đúng 2/2 unanswerable và không có generation error.
- Citation precision/recall giữ nguyên 0,400/0,375; Evidence-F1 giảm nhẹ
  0,425 -> 0,417; thời gian tăng 9,738 -> 10,508 giây/câu.
- Kết luận: giữ thay đổi vì tăng chất lượng answer rõ và không giảm an toàn hay
  citation; định dạng không thay thế việc cải thiện evidence selection.
- Báo cáo: `QASPER_ANSWER_EVALUATION.md`; log cục bộ:
  `results/qasper_answer_evaluation_20260928T082453Z.json`.
- 95 test passed; Ruff passed; còn một cảnh báo deprecation Starlette/httpx.
- Bước kế tiếp: tách các câu evidence đúng nhưng Answer-F1 còn thấp để đánh giá
  lỗi nội dung và độ đầy đủ; không tiếp tục sửa prompt theo từng câu riêng lẻ.

### Mới nhất: hiệu chỉnh evidence gate cho cross-encoder

- Đã mở rộng Evidence Gate để hiểu điểm của phương pháp cross-encoder nhưng
  không thay đổi gate hoặc retrieval mặc định của Agent.
- Quét 20 cấu hình trên nửa development và xác minh trên nửa paper còn lại,
  kèm negative ghép sai-paper; không dùng held-out.
- Chọn ngưỡng cross-encoder 0,50 và lexical overlap 3. Trên verification,
  balanced accuracy tăng rất nhẹ 0,7130 -> 0,7135, precision 0,514 -> 0,529,
  specificity 0,600 -> 0,644; recall giảm 0,826 -> 0,783.
- Kiểm tra mục tiêu 3 câu bị từ chối và 2 câu unanswerable: sửa được 1 câu với
  Answer-F1 0,902; 1 câu vẫn bị từ chối; 1 câu qua gate và dẫn đúng evidence
  nhưng Answer-F1 0,0; vẫn từ chối đúng 2/2 câu unanswerable.
- Kết luận: gate chỉ giải quyết một phần; không nên tiếp tục hạ ngưỡng. Lỗi còn
  lại nằm ở ranking/context và answer generation.
- Báo cáo: `EVIDENCE_GATE_CALIBRATION.md`; log cục bộ:
  `results/cross_encoder_gate_calibration.json`.
- 90 test passed; Ruff passed; còn một cảnh báo deprecation Starlette/httpx.
- Bước kế tiếp: cải thiện lựa chọn/diễn đạt câu trả lời từ evidence đã đúng,
  không tuning thêm gate trên cùng tập development.

### Mới nhất: thí nghiệm cross-encoder reranker trên QASPER development

- Chẩn đoán 8 retrieval miss cho thấy 7 câu vẫn có gold evidence trong top 20;
  vấn đề chính là xếp hạng chứ không phải mất chunk hay lỗi đọc dữ liệu.
- Đã thêm thí nghiệm rerank 20 ứng viên Hybrid + Ontology bằng
  `cross-encoder/ms-marco-MiniLM-L6-v2`, giữ nguyên các baseline cũ.
- Trên cùng 20 câu answerable development, Recall@5 tăng từ 0,600 (12/20)
  lên 0,850 (17/20), MRR tăng từ 0,424 lên 0,566; candidate recall@20 là 0,950.
- Reranker chạy CPU vì PyTorch trong `.venv` là bản CPU-only; Ollama vẫn dùng
  GPU độc lập. Chưa cần cài lại PyTorch CUDA cho model nhỏ này.
- Không mở hoặc chạy held-out. Đây là kết quả chọn hướng trên development,
  chưa phải kết quả cuối.
- Đã tích hợp thành phương pháp riêng `hybrid_ontology_cross_encoder`, giữ
  phương pháp cũ và mặc định Agent để phục vụ ablation.
- Đối chứng end-to-end cùng prompt mới: cross-encoder tăng Evidence-F1 từ
  0,425 lên 0,450 và citation P/R từ 0,400/0,375 lên 0,425/0,425, nhưng
  Answer-F1 giảm từ 0,349 xuống 0,292, số câu trả lời giảm 16 xuống 15 và
  thời gian tăng từ 9,738 lên 12,642 giây/câu.
- Vì retrieval tốt hơn chưa chuyển thành answer tốt hơn, Agent vẫn dùng
  `hybrid_ontology_rerank` mặc định; cross-encoder chỉ là tùy chọn thí nghiệm.
- Báo cáo: `CROSS_ENCODER_RERANKER.md`; log cục bộ:
  `results/qasper_cross_encoder_reranker.json`.
- 89 test passed; Ruff passed; còn một cảnh báo deprecation Starlette/httpx.
- Bước kế tiếp: phân tích sự lệch giữa retrieval metric và answer metric,
  đặc biệt evidence gate và lựa chọn top 3 đưa vào LLM; chưa đổi mặc định.

### Mới nhất: phân tích lỗi và cải thiện câu trả lời trực tiếp

- Đã thêm công cụ phân tích 22 case baseline thành các nhóm: 8 retrieval miss,
  7 lỗi nội dung/định dạng câu trả lời, 2 lỗi do chỉ đưa top 3 vào LLM, 1 lần
  evidence gate từ chối sai, 2 câu thành công và 2 lần từ chối đúng câu
  unanswerable.
- Đã bổ sung chế độ chọn `question_id` để chỉ chạy lại case development cần
  kiểm tra, không mở hoặc dùng held-out.
- Prompt Qwen3:4b nay yêu cầu trả lời trực tiếp trước: câu boolean bắt đầu bằng
  `Yes`/`No`; câu hỏi số, tên, task, metric hoặc danh sách nêu giá trị trước.
- Chạy lại đúng 7 case lỗi định dạng: Answer-F1 tăng từ 0,201 lên 0,563;
  Evidence-F1 tăng từ 0,690 lên 0,881; citation precision/recall đạt
  0,929/0,857; không có generation error, 2 câu đạt Answer-F1 1,0.
- Đây là phép so sánh development có chủ đích trên lỗi đã biết, không thay thế
  baseline 22 câu và không phải kết quả held-out. Nút thắt tiếp theo là 8
  retrieval miss, không còn chủ yếu là cách diễn đạt của LLM.
- Báo cáo: `QASPER_ANSWER_EVALUATION.md`; log chi tiết cục bộ:
  `results/qasper_answer_evaluation_20260927T120906Z.json`.
- 81 test passed; Ruff passed; còn một cảnh báo deprecation Starlette/httpx.
- Bước kế tiếp: sửa retrieval miss trên development bằng chẩn đoán theo từng
  phương pháp, không chỉnh theo held-out; sau đó chạy lại baseline lớn hơn.

### Mới nhất: baseline Answer-F1/Citation trên QASPER thật

- Đã tải lại QASPER train/dev v0.3 chính thức và xác minh SHA-256 khớp
  `a28fdf...b5a`; đủ 20/20 paper development hiện tại, không dùng held-out.
- Đã thêm bộ đọc reference answer theo evaluator chính thức: extractive,
  abstractive, boolean và unanswerable; tính Answer-F1 token và Evidence-F1.
- Đã thêm `scripts/evaluate_qasper_answers.py`, chạy toàn luồng document-scoped
  retrieval -> Ontology re-ranking -> evidence gate -> Qwen3:4b -> citation.
- Mẫu gồm 20 câu answerable từ 20 paper khác nhau. Trong chính 20 paper này chỉ
  có 2 câu mà mọi annotation đều là unanswerable, nên thực tế chạy 22 thay vì
  25 câu; Agent từ chối đúng 2/2 câu unanswerable tự nhiên.
- Trên 20 câu answerable: Answer-F1 0,246; Evidence-F1 0,358; citation precision
  0,300; citation recall 0,375; Agent trả lời 15 và từ chối 5.
- Toàn bộ 22 câu: Answer-F1 0,315; Evidence-F1 0,417; không có generation error;
  trung bình 13,081 giây/câu, cold case đầu 67,313 giây.
- Đây là baseline development, không phải điểm luận văn/held-out. Boolean answer
  còn dài dòng thay vì trả lời trực tiếp Yes/No; retrieval/citation vẫn là nút thắt.
- Báo cáo: `QASPER_ANSWER_EVALUATION.md`; log chi tiết cục bộ:
  `results/qasper_answer_evaluation_20260927T115655Z.json`.
- 79 test passed; Ruff passed; còn một cảnh báo deprecation Starlette/httpx.
- Bước kế tiếp: error analysis theo bốn nhóm retrieval miss, gate rejection,
  answer error, citation error; sau đó sửa direct-answer format trên development.

### Mới nhất: hiệu chỉnh Evidence Gate trên QASPER development

- Đã thêm cấu hình ngưỡng cho `EvidenceGate` và công cụ
  `scripts/calibrate_evidence_gate.py`; công cụ từ chối chạy trên held-out.
- Chia 20 paper development thành 10 paper chọn ngưỡng và 10 paper xác minh
  nội bộ. Một case được xem là có evidence khi gold QASPER nằm trong top 3 mà
  LLM nhận; ghép câu hỏi với paper kế tiếp để tạo case thiếu bằng chứng tổng hợp.
- Đã so 576 cấu hình. Trên 68 case xác minh, balanced accuracy tăng từ 0,549
  lên 0,657; specificity tăng từ 0,275 lên 0,490; recall giữ nguyên 0,824;
  false positive giảm từ 37 xuống 26 và false negative giữ nguyên 3.
- Ngưỡng được khóa: Ontology 0,80; Semantic 0,55 với overlap 2; nhánh kết hợp
  BM25 + Semantic dùng Semantic 0,40 với overlap 3.
- Đây là proxy development có negative sai-paper tổng hợp; precision mới 0,350,
  chưa đủ coi answerability đã giải quyết. Chưa dùng hoặc chạy lại held-out.
- Báo cáo: `EVIDENCE_GATE_CALIBRATION.md`; log chi tiết cục bộ:
  `results/evidence_gate_calibration.json`.
- 77 test passed; Ruff passed; còn một cảnh báo deprecation Starlette/httpx.
- Bước kế tiếp: đánh giá thủ công answer/citation trên mẫu QASPER lớn hơn và
  bổ sung câu unanswerable tự nhiên trước khi cân nhắc chạy held-out cuối cùng.

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
- [x] Đã có baseline development 22 câu đánh giá Answer-F1, Evidence-F1,
  citation precision/recall và unanswerable; chưa phải kết quả held-out cuối.
- [x] Đã tích hợp adapter và chạy end-to-end với LLM local thật trên QASPER.
- [~] AI Agent có nhánh Ollama, evidence gate và kiểm tra quote/ID; đã có đánh
  giá tự động bước đầu, còn cần đánh giá thủ công và tập thực nghiệm lớn hơn.
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
đánh giá khoa học cho Ontology/Agent.

1. Giữ nguyên kết quả held-out v3 và không tiếp tục tuning theo test này.
2. Thiết kế hướng concept linking khái quát hơn (candidate generation từ CSO hoặc zero-shot
   linking), dùng một development protocol mới nếu tiếp tục nghiên cứu retrieval.
3. Tiếp tục phân tích và cải thiện retrieval miss trên development; giữ nguyên
   held-out, sau đó xác nhận answer correctness/citation/unanswerable trên mẫu lớn hơn.
4. Đã hoàn thành reasoner consistency, 10 competency questions, rà soát CSO mapping
   và paired bootstrap trên development; tiếp theo thiết kế protocol mới để kiểm chứng
   khả năng khái quát mà không dùng lại held-out đã xem.

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
- AI Agent và answer generation: đã chạy Qwen3:4b cục bộ end-to-end trên QASPER
  thật, có baseline Answer-F1/Evidence-F1/citation và thử nghiệm direct-answer;
  chất lượng còn phụ thuộc mạnh vào retrieval và chưa phải kết quả held-out cuối.
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
