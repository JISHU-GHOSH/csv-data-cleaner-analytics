let activeChart = null;
let currentDataset = null;

// Table pagination, search, and sorting state
let searchQuery = "";
let currentPage = 1;
const pageSize = 20;
let sortColumn = null;
let sortDirection = "asc";

document.addEventListener("DOMContentLoaded", () => {
  fetchState();
  initDragAndDrop();
});

async function fetchState() {
  try {
    const res = await fetch("/api/state");
    const data = await res.json();
    renderState(data);
  } catch (err) {
    console.error("Error fetching state:", err);
  }
}

function renderState(data) {
  currentDataset = data;

  const homeView = document.getElementById("homeView");
  const editorView = document.getElementById("editorView");

  if (!data.has_data) {
    homeView.style.display = "block";
    editorView.style.display = "none";
    return;
  }

  homeView.style.display = "none";
  editorView.style.display = "block";

  document.getElementById("activeFileName").innerText = data.filename || "dataset.csv";
  document.getElementById("activeDimensions").innerText = `${data.total_rows} rows × ${data.columns.length} columns`;

  const m = data.metrics || {};
  const dupTag = document.getElementById("dupCountTag");
  const nullTag = document.getElementById("nullCountTag");

  dupTag.innerText = m.duplicate_count > 0 ? `${m.duplicate_count} duplicate rows` : "0 duplicates";
  dupTag.className = m.duplicate_count > 0 ? "tag red" : "tag green";

  nullTag.innerText = m.total_missing_cells > 0 ? `${m.total_missing_cells} missing cells` : "0 missing cells";
  nullTag.className = m.total_missing_cells > 0 ? "tag red" : "tag green";

  // Data Quality Meter
  const quality = m.quality_score !== undefined ? m.quality_score : 0;
  const qualityText = document.getElementById("qualityScoreText");
  const qualityFill = document.getElementById("qualityScoreFill");
  if (qualityText && qualityFill) {
    qualityText.innerText = `${quality}%`;
    qualityFill.style.width = `${quality}%`;
    if (quality >= 85) {
      qualityFill.style.backgroundColor = "#10B981"; // green
    } else if (quality >= 60) {
      qualityFill.style.backgroundColor = "#F59E0B"; // amber
    } else {
      qualityFill.style.backgroundColor = "#E5322D"; // red
    }
  }

  // Undo button state
  const undoBtn = document.getElementById("undoBtn");
  if (undoBtn) {
    undoBtn.disabled = !m.can_undo;
  }

  document.getElementById("dockStatusText").innerText =
    m.duplicate_count === 0 && m.total_missing_cells === 0
      ? "Dataset is 100% clean and ready for export."
      : "Data issues detected. Click 'Auto-Clean CSV' or select individual tools above.";

  applyTableFiltersAndRender();
  document.getElementById("auditViewer").innerText = data.report_text || "No cleaning actions performed yet.";

  populateColumnDropdowns(data.columns);
  updateStats();
  updateChart();
}

function applyTableFiltersAndRender() {
  if (!currentDataset || !currentDataset.rows) return;

  const rawRows = currentDataset.rows;
  const columns = currentDataset.columns || [];

  // 1. Search Filter
  let filtered = rawRows;
  if (searchQuery.trim() !== "") {
    const q = searchQuery.toLowerCase().trim();
    filtered = rawRows.filter(row => {
      for (const col of columns) {
        const val = row[col];
        if (val !== null && val !== undefined && String(val).toLowerCase().includes(q)) {
          return true;
        }
      }
      return false;
    });
  }

  // 2. Sorting
  if (sortColumn && columns.includes(sortColumn)) {
    filtered = [...filtered].sort((a, b) => {
      let va = a[sortColumn];
      let vb = b[sortColumn];

      if (va === null || va === undefined) return 1;
      if (vb === null || vb === undefined) return -1;

      const numA = Number(va);
      const numB = Number(vb);
      if (!isNaN(numA) && !isNaN(numB)) {
        return sortDirection === "asc" ? numA - numB : numB - numA;
      }

      const strA = String(va).toLowerCase();
      const strB = String(vb).toLowerCase();
      if (strA < strB) return sortDirection === "asc" ? -1 : 1;
      if (strA > strB) return sortDirection === "asc" ? 1 : -1;
      return 0;
    });
  }

  // 3. Pagination
  const totalRows = filtered.length;
  const totalPages = Math.max(1, Math.ceil(totalRows / pageSize));
  if (currentPage > totalPages) currentPage = totalPages;
  if (currentPage < 1) currentPage = 1;

  const startIdx = (currentPage - 1) * pageSize;
  const endIdx = Math.min(startIdx + pageSize, totalRows);
  const pageRows = totalRows > 0 ? filtered.slice(startIdx, endIdx) : [];

  // Update pagination info controls
  const paginationLabel = document.getElementById("paginationLabel");
  const prevBtn = document.getElementById("prevPageBtn");
  const nextBtn = document.getElementById("nextPageBtn");

  if (paginationLabel) {
    if (totalRows === 0) {
      paginationLabel.innerText = "No matching rows found";
    } else {
      paginationLabel.innerText = `Showing ${startIdx + 1}–${endIdx} of ${totalRows} rows (Page ${currentPage} of ${totalPages})`;
    }
  }

  if (prevBtn) prevBtn.disabled = currentPage <= 1;
  if (nextBtn) nextBtn.disabled = currentPage >= totalPages || totalRows === 0;

  // Render Table
  renderTableSlice(columns, pageRows, startIdx);
}

function renderTableSlice(columns, rows, offset) {
  const container = document.getElementById("tableContainer");
  if (!rows || rows.length === 0) {
    container.innerHTML = '<div style="padding: 24px; text-align: center; color: #888;">No rows match your criteria.</div>';
    return;
  }

  let html = '<table><thead><tr>';
  html += '<th class="row-index">#</th>';

  columns.forEach(col => {
    let sortIcon = '↕';
    if (sortColumn === col) {
      sortIcon = sortDirection === "asc" ? '▲' : '▼';
    }
    html += `<th class="sortable" onclick="handleSort('${escapeHtml(col)}')">${escapeHtml(col)} <span class="sort-icon">${sortIcon}</span></th>`;
  });
  html += '</tr></thead><tbody>';

  rows.forEach((row, idx) => {
    html += '<tr>';
    html += `<td class="row-index">${offset + idx + 1}</td>`;
    columns.forEach(col => {
      const val = row[col];
      if (val === null || val === undefined) {
        html += '<td><span class="nan-cell">NaN</span></td>';
      } else {
        html += `<td>${escapeHtml(val)}</td>`;
      }
    });
    html += '</tr>';
  });

  html += '</tbody></table>';
  container.innerHTML = html;
}

function onSearchInput() {
  const input = document.getElementById("tableSearchInput");
  searchQuery = input ? input.value : "";
  currentPage = 1;
  applyTableFiltersAndRender();
}

function handleSort(col) {
  if (sortColumn === col) {
    sortDirection = sortDirection === "asc" ? "desc" : "asc";
  } else {
    sortColumn = col;
    sortDirection = "asc";
  }
  applyTableFiltersAndRender();
}

function prevPage() {
  if (currentPage > 1) {
    currentPage--;
    applyTableFiltersAndRender();
  }
}

function nextPage() {
  currentPage++;
  applyTableFiltersAndRender();
}

function populateColumnDropdowns(columns) {
  const chartCol = document.getElementById("chartColumn");
  const missingCol = document.getElementById("missingCol");
  const dropCol = document.getElementById("dropColSelect");
  const outlierCol = document.getElementById("outlierColSelect");

  if (chartCol) {
    const prev = chartCol.value;
    chartCol.innerHTML = "";
    columns.forEach(col => {
      const opt = document.createElement("option");
      opt.value = col;
      opt.innerText = col;
      chartCol.appendChild(opt);
    });
    if (columns.includes(prev)) chartCol.value = prev;
  }

  if (missingCol) {
    missingCol.innerHTML = '<option value="all">All Columns</option>';
    columns.forEach(col => {
      const opt = document.createElement("option");
      opt.value = col;
      opt.innerText = col;
      missingCol.appendChild(opt);
    });
  }

  if (dropCol) {
    dropCol.innerHTML = "";
    columns.forEach(col => {
      const opt = document.createElement("option");
      opt.value = col;
      opt.innerText = col;
      dropCol.appendChild(opt);
    });
  }

  if (outlierCol) {
    outlierCol.innerHTML = "";
    columns.forEach(col => {
      const opt = document.createElement("option");
      opt.value = col;
      opt.innerText = col;
      outlierCol.appendChild(opt);
    });
  }
}

function initDragAndDrop() {
  window.addEventListener("dragover", e => e.preventDefault());
  window.addEventListener("drop", e => {
    e.preventDefault();
    if (e.dataTransfer && e.dataTransfer.files.length > 0) {
      const file = e.dataTransfer.files[0];
      if (file.name.endsWith(".csv")) {
        uploadFileObject(file);
      } else {
        showToast("Please drop a valid .csv file.");
      }
    }
  });
}

async function loadSample(sampleName) {
  showToast(`Loading ${sampleName} sample...`);
  try {
    const res = await fetch("/api/load-sample", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ sample: sampleName })
    });
    const result = await res.json();
    if (result.success) {
      searchQuery = "";
      if (document.getElementById("tableSearchInput")) {
        document.getElementById("tableSearchInput").value = "";
      }
      currentPage = 1;
      sortColumn = null;
      renderState(result.data);
      showToast(result.message);
    } else {
      showToast(result.message);
    }
  } catch (err) {
    showToast("Error loading sample dataset.");
  }
}

async function uploadCSV(event) {
  const file = event.target.files[0];
  if (!file) return;
  await uploadFileObject(file);
  event.target.value = "";
}

async function uploadFileObject(file) {
  const formData = new FormData();
  formData.append("file", file);

  showToast(`Uploading ${file.name}...`);
  try {
    const res = await fetch("/api/upload", {
      method: "POST",
      body: formData
    });
    const result = await res.json();
    if (result.success) {
      searchQuery = "";
      if (document.getElementById("tableSearchInput")) {
        document.getElementById("tableSearchInput").value = "";
      }
      currentPage = 1;
      sortColumn = null;
      renderState(result.data);
      showToast(`Uploaded ${file.name} successfully.`);
    } else {
      showToast(result.message);
    }
  } catch (err) {
    showToast("Error uploading CSV file.");
  }
}

async function triggerClean(action, params = {}) {
  showToast("Applying cleaning operation...");
  try {
    const res = await fetch("/api/clean", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action, ...params })
    });
    const result = await res.json();
    if (result.success) {
      renderState(result.data);
      showToast(result.message);
    } else {
      showToast(result.message);
    }
  } catch (err) {
    showToast("Operation failed.");
  }
}

async function triggerUndo() {
  showToast("Undoing last operation...");
  try {
    const res = await fetch("/api/undo", { method: "POST" });
    const result = await res.json();
    if (result.success) {
      renderState(result.data);
      showToast("Reverted last change.");
    } else {
      showToast(result.message);
    }
  } catch (err) {
    showToast("Undo request failed.");
  }
}

async function resetData() {
  showToast("Restoring original data...");
  try {
    const res = await fetch("/api/reset", { method: "POST" });
    const result = await res.json();
    if (result.success) {
      renderState(result.data);
      showToast("Restored original dataset.");
    } else {
      showToast(result.message);
    }
  } catch (err) {
    showToast("Reset failed.");
  }
}

function resetToHome() {
  document.getElementById("homeView").style.display = "block";
  document.getElementById("editorView").style.display = "none";
}

function openDirectTool(toolName) {
  if (!currentDataset || !currentDataset.has_data) {
    loadSample("students").then(() => {
      executeToolAction(toolName);
    });
  } else {
    executeToolAction(toolName);
  }
}

function executeToolAction(toolName) {
  if (toolName === "auto_clean") {
    triggerClean("auto_clean");
    switchEditorTab("gridTab");
  } else if (toolName === "remove_duplicates") {
    triggerClean("remove_duplicates");
    switchEditorTab("gridTab");
  } else if (toolName === "standardize_headers") {
    triggerClean("standardize_headers");
    switchEditorTab("gridTab");
  } else if (toolName === "handle_missing") {
    openMissingModal();
  } else if (toolName === "outliers") {
    openOutliersModal();
  } else if (toolName === "stats") {
    switchEditorTab("statsTab");
  } else if (toolName === "charts") {
    switchEditorTab("chartTab");
  }
}

function switchEditorTab(tabId) {
  document.querySelectorAll(".editor-pane").forEach(p => p.style.display = "none");
  document.querySelectorAll(".action-strip .strip-btn").forEach(b => b.classList.remove("active"));

  const targetPane = document.getElementById(tabId);
  if (targetPane) {
    targetPane.style.display = "block";
  }

  if (tabId === "gridTab") document.getElementById("tabGridBtn")?.classList.add("active");
  if (tabId === "statsTab") document.getElementById("tabStatsBtn")?.classList.add("active");
  if (tabId === "chartTab") {
    document.getElementById("tabChartBtn")?.classList.add("active");
    setTimeout(updateChart, 50);
  }
  if (tabId === "logTab") document.getElementById("tabLogBtn")?.classList.add("active");
}

function downloadCleanCSV() {
  if (!currentDataset || !currentDataset.has_data) {
    showToast("No dataset loaded to export.");
    return;
  }
  window.location.href = "/api/export/csv";
}

function downloadCleanJSON() {
  if (!currentDataset || !currentDataset.has_data) {
    showToast("No dataset loaded to export.");
    return;
  }
  window.location.href = "/api/export/json";
}

function downloadReport() {
  if (!currentDataset || !currentDataset.has_data) {
    showToast("No dataset loaded to export.");
    return;
  }
  window.location.href = "/api/export/report";
}

async function updateStats() {
  const container = document.getElementById("statsContainer");
  if (!currentDataset || !currentDataset.has_data) {
    container.innerHTML = '<div style="padding: 24px; text-align: center; color: #888;">Load a dataset to view statistics.</div>';
    return;
  }

  try {
    const res = await fetch("/api/stats");
    const data = await res.json();

    let html = '<div style="display:flex; flex-direction:column; gap:20px;">';

    if (data.numeric && Object.keys(data.numeric).length > 0) {
      html += '<div><h4 style="margin-bottom:10px; font-size:14px; font-weight:700; color:#161616;">Five-Number Numerical Summary</h4>';
      html += '<div class="sheet-container"><table><thead><tr><th>Metric</th>';
      const cols = Object.keys(data.numeric);
      cols.forEach(c => html += `<th>${escapeHtml(c)}</th>`);
      html += '</tr></thead><tbody>';

      const metrics = ["count", "mean", "std", "min", "25%", "50%", "75%", "max"];
      metrics.forEach(m => {
        html += `<tr><td><strong>${m}</strong></td>`;
        cols.forEach(c => {
          const val = data.numeric[c][m];
          html += `<td>${val !== undefined ? val : "-"}</td>`;
        });
        html += '</tr>';
      });
      html += '</tbody></table></div></div>';
    }

    if (data.categorical && Object.keys(data.categorical).length > 0) {
      html += '<div><h4 style="margin-bottom:10px; font-size:14px; font-weight:700; color:#161616;">Categorical Frequencies</h4>';
      for (const [col, rows] of Object.entries(data.categorical)) {
        html += `<div style="margin-bottom: 14px;"><h5 style="margin-bottom:6px; font-size:13px; color:#555;">Column: <strong>${escapeHtml(col)}</strong></h5>`;
        html += '<div class="sheet-container" style="max-height: 180px;"><table><thead><tr><th>Category</th><th>Count</th><th>Percentage</th></tr></thead><tbody>';
        rows.forEach(r => {
          html += `<tr><td>${escapeHtml(r.category)}</td><td>${r.count}</td><td><span style="color:#16A34A; font-weight:600;">${r.percentage}%</span></td></tr>`;
        });
        html += '</tbody></table></div></div>';
      }
      html += '</div>';
    }

    html += '</div>';
    container.innerHTML = html;
  } catch (err) {
    console.error("Error updating stats:", err);
  }
}

async function updateChart() {
  const colElem = document.getElementById("chartColumn");
  const typeElem = document.getElementById("chartType");
  if (!colElem || !typeElem) return;

  const col = colElem.value;
  const chartType = typeElem.value;
  if (!col) return;

  try {
    const res = await fetch(`/api/chart-data?column=${encodeURIComponent(col)}&type=${chartType}`);
    const data = await res.json();

    const canvas = document.getElementById("analyticsChart");
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (activeChart) {
      activeChart.destroy();
    }

    activeChart = new Chart(ctx, {
      type: "bar",
      data: {
        labels: data.labels,
        datasets: [{
          label: col,
          data: data.values,
          backgroundColor: "#E5322D",
          hoverBackgroundColor: "#C5221F",
          borderColor: "#E5322D",
          borderWidth: 1,
          borderRadius: 4
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          title: {
            display: true,
            text: `Distribution of ${col}`,
            font: { size: 14, weight: "bold" },
            color: "#161616"
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            grid: { color: "#F3F4F6" },
            ticks: { color: "#666" }
          },
          x: {
            grid: { display: false },
            ticks: { color: "#666" }
          }
        }
      }
    });
  } catch (err) {
    console.error("Error updating chart:", err);
  }
}

// Modal Handlers
function openModal(id) {
  const m = document.getElementById(id);
  if (m) m.style.display = "flex";
}

function closeModal(id) {
  const m = document.getElementById(id);
  if (m) m.style.display = "none";
}

function openMissingModal() {
  if (!currentDataset || !currentDataset.has_data) {
    showToast("Please select a CSV file first.");
    return;
  }
  openModal("missingModal");
}

function closeMissingModal() {
  closeModal("missingModal");
}

function toggleCustomVal() {
  const strat = document.getElementById("missingStrategy").value;
  const group = document.getElementById("customValGroup");
  group.style.display = strat === "custom" ? "flex" : "none";
}

function applyMissingStrategy() {
  const col = document.getElementById("missingCol").value;
  const strategy = document.getElementById("missingStrategy").value;
  const customVal = document.getElementById("customValInput").value;

  closeModal("missingModal");
  triggerClean("handle_missing", { column: col, strategy, custom_val: customVal });
}

function openDropColModal() {
  if (!currentDataset || !currentDataset.has_data) {
    showToast("Please select a CSV file first.");
    return;
  }
  openModal("dropColModal");
}

function applyDropColumn() {
  const col = document.getElementById("dropColSelect").value;
  if (!col) return;
  closeModal("dropColModal");
  triggerClean("drop_column", { column: col });
}

function openOutliersModal() {
  if (!currentDataset || !currentDataset.has_data) {
    showToast("Please select a CSV file first.");
    return;
  }
  openModal("outliersModal");
}

function applyRemoveOutliers() {
  const col = document.getElementById("outlierColSelect").value;
  if (!col) return;
  closeModal("outliersModal");
  triggerClean("remove_outliers", { column: col });
}

function showToast(msg) {
  const toast = document.getElementById("toastNotification");
  if (!toast) return;
  toast.innerText = msg;
  toast.classList.add("show");
  setTimeout(() => toast.classList.remove("show"), 2800);
}

function escapeHtml(str) {
  if (typeof str !== "string") return str;
  return str.replace(/[&<>"']/g, m => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[m]);
}