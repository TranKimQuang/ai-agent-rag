const pdfInput = document.querySelector("#pdfInput");
const fileLabel = document.querySelector("#fileLabel");
const dropZone = document.querySelector("#dropZone");
const uploadButton = document.querySelector("#uploadButton");
const uploadResult = document.querySelector("#uploadResult");
const searchForm = document.querySelector("#searchForm");
const question = document.querySelector("#question");
const results = document.querySelector("#results");
const emptyState = document.querySelector("#emptyState");
const resultList = document.querySelector("#resultList");
const resultCount = document.querySelector("#resultCount");
const activeMethod = document.querySelector("#activeMethod");
const ontologyStrip = document.querySelector("#ontologyStrip");
const resultTemplate = document.querySelector("#resultTemplate");
const toast = document.querySelector("#toast");

let selectedFile = null;

// Always start the demo with the project's recommended retrieval method.
document.querySelector('input[name="method"][value="hybrid_ontology"]').checked = true;

function setFile(file) {
  if (!file) return;
  if (file.type !== "application/pdf" && !file.name.toLowerCase().endsWith(".pdf")) {
    showToast("Vui lòng chọn đúng tệp PDF.", true);
    return;
  }
  selectedFile = file;
  fileLabel.textContent = file.name;
  uploadButton.disabled = false;
}

pdfInput.addEventListener("change", () => setFile(pdfInput.files[0]));

["dragenter", "dragover"].forEach((eventName) => {
  dropZone.addEventListener(eventName, (event) => {
    event.preventDefault();
    dropZone.classList.add("dragging");
  });
});

["dragleave", "drop"].forEach((eventName) => {
  dropZone.addEventListener(eventName, (event) => {
    event.preventDefault();
    dropZone.classList.remove("dragging");
  });
});

dropZone.addEventListener("drop", (event) => setFile(event.dataTransfer.files[0]));

uploadButton.addEventListener("click", async () => {
  if (!selectedFile) return;
  setLoading(uploadButton, true, "Đang lập chỉ mục");
  try {
    const response = await fetch("/documents", {
      method: "POST",
      headers: {
        "Content-Type": "application/pdf",
        "X-Filename": encodeURIComponent(selectedFile.name),
      },
      body: selectedFile,
    });
    const data = await parseResponse(response);
    uploadResult.innerHTML = `
      <strong>Đã lập chỉ mục thành công</strong>
      ${escapeHtml(data.filename)} · ${data.pages} trang · ${data.chunks} chunk<br />
      ${data.concept_links} liên kết concept được tạo.
    `;
    uploadResult.classList.remove("hidden");
    showToast("Tài liệu đã sẵn sàng để tìm kiếm.");
  } catch (error) {
    showToast(error.message, true);
  } finally {
    setLoading(uploadButton, false, "Tạo chỉ mục tài liệu");
  }
});

searchForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const submitButton = searchForm.querySelector("button[type='submit']");
  const method = new FormData(searchForm).get("method");
  const query = question.value.trim();
  if (query.length < 2) return;

  setLoading(submitButton, true, "Đang truy hồi");
  try {
    const params = new URLSearchParams({ q: query, limit: "5", method });
    const response = await fetch(`/search?${params}`);
    const data = await parseResponse(response);
    renderResults(data);
  } catch (error) {
    showToast(error.message, true);
  } finally {
    setLoading(submitButton, false, "Tìm bằng chứng");
  }
});

function renderResults(data) {
  resultList.replaceChildren();
  emptyState.classList.add("hidden");
  results.classList.remove("hidden");
  resultCount.textContent = data.results.length;
  activeMethod.textContent = methodLabel(data.method);

  const first = data.results[0];
  if (first?.query_concepts?.length) {
    const concepts = first.query_concepts.map(escapeHtml).join(", ");
    const expanded = first.expanded_query ? ` · Truy vấn mở rộng: ${escapeHtml(first.expanded_query)}` : "";
    ontologyStrip.innerHTML = `<b>Ontology nhận diện:</b> ${concepts}${expanded}`;
    ontologyStrip.classList.remove("hidden");
  } else {
    ontologyStrip.classList.add("hidden");
  }

  if (!data.results.length) {
    resultList.innerHTML = `<div class="empty-state"><h3>Chưa tìm thấy bằng chứng</h3><p>Hãy thử cách diễn đạt khác hoặc tải thêm tài liệu phù hợp.</p></div>`;
    return;
  }

  data.results.forEach((item, index) => {
    const card = resultTemplate.content.cloneNode(true);
    card.querySelector(".rank").textContent = index + 1;
    card.querySelector(".source").textContent = item.filename;
    card.querySelector(".page").textContent = `Trang ${item.page}`;
    card.querySelector(".score").textContent = `Điểm ${formatScore(item.score)}`;
    card.querySelector(".evidence").textContent = item.text;

    const conceptBox = card.querySelector(".concepts");
    (item.chunk_concepts || []).slice(0, 6).forEach((concept) => {
      const tag = document.createElement("span");
      tag.textContent = concept;
      conceptBox.append(tag);
    });

    card.querySelector(".score-grid").innerHTML = [
      ["BM25", item.bm25_score],
      ["Semantic", item.semantic_score],
      ["Ontology", item.ontology_score],
    ].map(([label, value]) => `<span>${label}<b>${formatScore(value)}</b></span>`).join("");

    const explanation = card.querySelector(".explanation");
    explanation.textContent = item.ontology_explanation || "Phương pháp này không sử dụng tín hiệu Ontology cho kết quả trên.";
    resultList.append(card);
  });
}

async function parseResponse(response) {
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || "Không thể xử lý yêu cầu.");
  }
  return data;
}

function setLoading(button, loading, text) {
  button.disabled = loading;
  button.classList.toggle("loading", loading);
  button.querySelector("span").textContent = text;
}

function formatScore(value) {
  if (value === null || value === undefined) return "—";
  return Number(value).toFixed(3);
}

function methodLabel(method) {
  return {
    bm25: "BM25",
    semantic: "Semantic",
    hybrid: "Hybrid · RRF",
    hybrid_ontology: "Hybrid + Ontology",
  }[method] || method;
}

function showToast(message, isError = false) {
  toast.textContent = message;
  toast.classList.toggle("error", isError);
  toast.classList.remove("hidden");
  window.clearTimeout(showToast.timeout);
  showToast.timeout = window.setTimeout(() => toast.classList.add("hidden"), 4200);
}

function escapeHtml(value) {
  const element = document.createElement("span");
  element.textContent = value ?? "";
  return element.innerHTML;
}
