// Global Application State
let activeChart = null;
let currentDataset = null;
let activeSampleKey = null;

// Table pagination, search, and sorting state
let searchQuery = "";
let currentPage = 1;
const pageSize = 20;
let sortColumn = null;
let sortDirection = "asc";

// Session ID persistence across page navigations
function getSessionId() {
  let sid = sessionStorage.getItem("cleaner_session_id");
  if (!sid) {
    sid = "sess-" + Math.random().toString(36).substring(2, 15) + "-" + Date.now();
    sessionStorage.setItem("cleaner_session_id", sid);
  }
  return sid;
}

function getFetchHeaders(extra = {}) {
  return {
    "X-Session-ID": getSessionId(),
    ...extra
  };
}

document.addEventListener("DOMContentLoaded", () => {
  fetchState();
  initDragAndDrop();
  initResponsiveHandlers();
});

function initResponsiveHandlers() {
  window.addEventListener("resize", () => {
    if (activeChart) {
      activeChart.resize();
    }
  });
}

async function fetchState() {
  try {
    const res = await fetch("/api/state", {
      headers: getFetchHeaders()
    });
    const data = await res.json();
    if (data.session_id) {
      sessionStorage.setItem("cleaner_session_id", data.session_id);
    }
    // Only auto-render editor if this specific browser session had data
    if (data.has_data && sessionStorage.getItem("cleaner_has_active_dataset") === "true") {
      renderState(data);
    } else {
      resetToHome();
    }
  } catch (err) {
    console.error("Error fetching state:", err);
    resetToHome();
  }
}

function renderState(data) {
  currentDataset = data;

  const homeView = document.getElementById("homeView");
  const editorView = document.getElementById("editorView");

  if (!data || !data.has_data) {
    sessionStorage.removeItem("cleaner_has_active_dataset");
    if (homeView) homeView.style.display = "block";
    if (editorView) editorView.style.display = "none";
    updateNavActive(null);
    return;
  }

  sessionStorage.setItem("cleaner_has_active_dataset", "true");
  if (homeView) homeView.style.display = "none";
  if (editorView) editorView.style.display = "block";

  updateNavActive(activeSampleKey || "editor");

  const fileNameElem = document.getElementById("activeFileName");
  if (fileNameElem) fileNameElem.innerText = data.filename || "dataset.csv";

  const dimElem = document.getElementById("activeDimensions");
  if (dimElem) dimElem.innerText = `${data.total_rows} rows × ${(data.columns || []).length} columns`;

  const m = data.metrics || {};
  const dupTag = document.getElementById("dupCountTag");
  const nullTag = document.getElementById("nullCountTag");

  if (dupTag) {
    dupTag.innerText = (m.duplicate_count || 0) > 0 ? `${m.duplicate_count} duplicate rows` : "0 duplicates";
    dupTag.className = (m.duplicate_count || 0) > 0 ? "tag red" : "tag green";
  }

  if (nullTag) {
    nullTag.innerText = (m.total_missing_cells || 0) > 0 ? `${m.total_missing_cells} missing cells` : "0 missing cells";
    nullTag.className = (m.total_missing_cells || 0) > 0 ? "tag red" : "tag green";
  }

  // Data Quality Score Meter
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

  const dockStatus = document.getElementById("dockStatusText");
  if (dockStatus) {
    dockStatus.innerText =
      (m.duplicate_count === 0 && m.total_missing_cells === 0)
        ? "Dataset is 100% clean and ready for export."
        : "Data defects detected. Click 'Auto-Clean CSV' or select individual tools above.";
  }

  applyTableFiltersAndRender();

  const auditViewer = document.getElementById("auditViewer");
  if (auditViewer) {
    auditViewer.innerText = data.report_text || "No cleaning actions performed yet.";
  }

  populateColumnDropdowns(data.columns, data.metrics);
  updateStats();
  updateChart();
}

function updateNavActive(key) {
  const menuButtons = document.querySelectorAll(".ilove-menu .menu-item");
  menuButtons.forEach(btn => btn.classList.remove("active"));

  if (!key || key === "home") {
    document.getElementById("navAllTools")?.classList.add("active");
  } else if (key === "students") {
    document.getElementById("navStudents")?.classList.add("active");
  } else if (key === "sales") {
    document.getElementById("navSales")?.classList.add("active");
  }
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

  renderTableSlice(columns, pageRows, startIdx);
}

function renderTableSlice(columns, rows, offset) {
  const container = document.getElementById("tableContainer");
  if (!container) return;

  if (!rows || rows.length === 0) {
    container.innerHTML = '<div style="padding: 32px; text-align: center; color: #888;">No rows match your criteria.</div>';
    return;
  }

  let html = '<table><thead><tr>';
  html += '<th class="row-index">#</th>';

  columns.forEach(col => {
    let sortIcon = '↕';
    if (sortColumn === col) {
      sortIcon = sortDirection === "asc" ? '▲' : '▼';
    }
    const cleanHeader = escapeHtml(col).trim();
    html += `<th class="sortable" onclick="handleSort('${escapeAttribute(col)}')">${cleanHeader} <span class="sort-icon">${sortIcon}</span></th>`;
  });
  html += '</tr></thead><tbody>';

  rows.forEach((row, idx) => {
    html += '<tr>';
    html += `<td class="row-index">${offset + idx + 1}</td>`;
    columns.forEach(col => {
      const val = row[col];
      if (val === null || val === undefined || val === "NaN" || val === "nan") {
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

function isColumnNumeric(col, metrics) {
  if (metrics && metrics.dtypes && metrics.dtypes[col]) {
    const dt = String(metrics.dtypes[col]).toLowerCase();
    return dt.includes("int") || dt.includes("float") || dt.includes("number");
  }
  if (!currentDataset || !currentDataset.rows || currentDataset.rows.length === 0) return true;
  let numericHits = 0;
  let totalChecked = 0;
  for (const row of currentDataset.rows) {
    const val = row[col];
    if (val !== null && val !== undefined && val !== "" && val !== "NaN") {
      totalChecked++;
      if (!isNaN(Number(val))) numericHits++;
    }
  }
  return totalChecked > 0 && (numericHits / totalChecked) >= 0.75;
}

function populateColumnDropdowns(columns, metrics) {
  const chartCol = document.getElementById("chartColumn");
  const missingCol = document.getElementById("missingCol");
  const dropCol = document.getElementById("dropColSelect");
  const outlierCol = document.getElementById("outlierColSelect");

  if (!columns || columns.length === 0) return;

  // 1. Chart Column Dropdown
  if (chartCol) {
    const prev = chartCol.value;
    chartCol.innerHTML = "";
    columns.forEach(col => {
      const opt = document.createElement("option");
      opt.value = col;
      opt.innerText = col.trim();
      chartCol.appendChild(opt);
    });
    if (columns.includes(prev)) {
      chartCol.value = prev;
    } else {
      // Default to first numeric column if available
      const firstNum = columns.find(c => isColumnNumeric(c, metrics));
      chartCol.value = firstNum || columns[0];
    }
  }

  // 2. Missing Value Column Dropdown
  if (missingCol) {
    const prev = missingCol.value;
    missingCol.innerHTML = '<option value="all">All Columns</option>';
    columns.forEach(col => {
      const opt = document.createElement("option");
      opt.value = col;
      opt.innerText = col.trim();
      missingCol.appendChild(opt);
    });
    if (prev && (prev === "all" || columns.includes(prev))) {
      missingCol.value = prev;
    }
  }

  // 3. Drop Column Dropdown
  if (dropCol) {
    dropCol.innerHTML = "";
    columns.forEach(col => {
      const opt = document.createElement("option");
      opt.value = col;
      opt.innerText = col.trim();
      dropCol.appendChild(opt);
    });
  }

  // 4. Outlier Column Dropdown: FILTER TO NUMERIC ONLY!
  if (outlierCol) {
    outlierCol.innerHTML = "";
    const numericCols = columns.filter(c => isColumnNumeric(c, metrics));
    const targetList = numericCols.length > 0 ? numericCols : columns;

    targetList.forEach(col => {
      const opt = document.createElement("option");
      opt.value = col;
      opt.innerText = col.trim();
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
  activeSampleKey = sampleName;
  try {
    const res = await fetch("/api/load-sample", {
      method: "POST",
      headers: getFetchHeaders({ "Content-Type": "application/json" }),
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
      showToast(result.message || "Failed to load sample.");
    }
  } catch (err) {
    showToast("Error loading sample dataset.");
  }
}

async function uploadCSV(event) {
  const file = event.target.files[0];
  if (!file) return;
  activeSampleKey = null;
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
      headers: { "X-Session-ID": getSessionId() },
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
      showToast(result.message || "Upload failed.");
    }
  } catch (err) {
    showToast("Error uploading CSV file.");
  }
}

// Convert client dataset to raw CSV string for server re-hydration backup
function serializeCurrentDatasetToCSV() {
  if (!currentDataset || !currentDataset.rows || !currentDataset.columns) return "";
  const cols = currentDataset.columns;
  let csv = cols.map(c => `"${c.replace(/"/g, '""')}"`).join(",") + "\n";
  for (const row of currentDataset.rows) {
    const line = cols.map(c => {
      const val = row[c];
      if (val === null || val === undefined) return "";
      return `"${String(val).replace(/"/g, '""')}"`;
    }).join(",");
    csv += line + "\n";
  }
  return csv;
}

async function triggerClean(action, params = {}) {
  showToast("Applying cleaning operation...");
  try {
    const payload = {
      action,
      ...params,
      current_csv: serializeCurrentDatasetToCSV(),
      source_name: currentDataset ? currentDataset.filename : "dataset.csv"
    };

    const res = await fetch("/api/clean", {
      method: "POST",
      headers: getFetchHeaders({ "Content-Type": "application/json" }),
      body: JSON.stringify(payload)
    });
    const result = await res.json();
    if (result.success) {
      renderState(result.data);
      showToast(result.message);
    } else {
      showToast(result.message || "Operation failed.");
    }
  } catch (err) {
    showToast("Operation request failed.");
  }
}

async function triggerUndo() {
  showToast("Undoing last operation...");
  try {
    const res = await fetch("/api/undo", {
      method: "POST",
      headers: getFetchHeaders()
    });
    const result = await res.json();
    if (result.success) {
      renderState(result.data);
      showToast("Reverted last change.");
    } else {
      showToast(result.message || "Undo failed.");
    }
  } catch (err) {
    showToast("Undo request failed.");
  }
}

async function resetData() {
  showToast("Restoring original data...");
  try {
    const res = await fetch("/api/reset", {
      method: "POST",
      headers: getFetchHeaders()
    });
    const result = await res.json();
    if (result.success) {
      renderState(result.data);
      showToast("Restored original dataset.");
    } else {
      showToast(result.message || "Reset failed.");
    }
  } catch (err) {
    showToast("Reset failed.");
  }
}

function resetToHome() {
  sessionStorage.removeItem("cleaner_has_active_dataset");
  const home = document.getElementById("homeView");
  const editor = document.getElementById("editorView");
  if (home) home.style.display = "block";
  if (editor) editor.style.display = "none";
  updateNavActive("home");
}

function openDirectTool(toolName) {
  if (!currentDataset || !currentDataset.has_data) {
    loadSample("students").then(() => {
      setTimeout(() => executeToolAction(toolName), 120);
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
    setTimeout(updateChart, 40);
  }
  if (tabId === "logTab") document.getElementById("tabLogBtn")?.classList.add("active");
}

// 100% Reliable Client-Side Export via Blob (Bypasses serverless dropouts)
function downloadCleanCSV() {
  if (!currentDataset || !currentDataset.rows || currentDataset.rows.length === 0) {
    showToast("No dataset loaded to export.");
    return;
  }
  const csvContent = serializeCurrentDatasetToCSV();
  const blob = new Blob(["\uFEFF" + csvContent], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  const baseName = (currentDataset.filename || "dataset.csv").replace(/\.csv$/i, "");
  a.href = url;
  a.download = `cleaned_${baseName}.csv`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
  showToast(`Downloaded cleaned_${baseName}.csv successfully.`);
}

function downloadCleanJSON() {
  if (!currentDataset || !currentDataset.rows || currentDataset.rows.length === 0) {
    showToast("No dataset loaded to export.");
    return;
  }
  const jsonStr = JSON.stringify(currentDataset.rows, null, 2);
  const blob = new Blob([jsonStr], { type: "application/json;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  const baseName = (currentDataset.filename || "dataset").replace(/\.csv$/i, "");
  a.href = url;
  a.download = `cleaned_${baseName}.json`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
  showToast(`Downloaded cleaned_${baseName}.json successfully.`);
}

function downloadReport() {
  const text = (currentDataset && currentDataset.report_text) ? currentDataset.report_text : "No audit entries recorded.";
  const blob = new Blob([text], { type: "text/plain;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "cleaning_audit_report.txt";
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
  showToast("Downloaded cleaning_audit_report.txt successfully.");
}

async function updateStats() {
  const container = document.getElementById("statsContainer");
  if (!container) return;

  if (!currentDataset || !currentDataset.has_data) {
    container.innerHTML = '<div style="padding: 24px; text-align: center; color: #888;">Load a dataset to view statistics.</div>';
    return;
  }

  try {
    const res = await fetch("/api/stats", {
      headers: getFetchHeaders()
    });
    const data = await res.json();

    let html = '<div style="display:flex; flex-direction:column; gap:20px;">';

    if (data.numeric && Object.keys(data.numeric).length > 0) {
      html += '<div><h4 style="margin-bottom:10px; font-size:14px; font-weight:700; color:#161616;">Five-Number Numerical Summary</h4>';
      html += '<div class="sheet-container"><table><thead><tr><th>Metric</th>';
      const cols = Object.keys(data.numeric);
      cols.forEach(c => html += `<th>${escapeHtml(c).trim()}</th>`);
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
        html += `<div style="margin-bottom: 14px;"><h5 style="margin-bottom:6px; font-size:13px; color:#555;">Column: <strong>${escapeHtml(col).trim()}</strong></h5>`;
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

// Client-Driven High-Speed Charting (Instant, zero-latency, 100% reliable)
function updateChart() {
  const colElem = document.getElementById("chartColumn");
  const typeElem = document.getElementById("chartType");
  const canvas = document.getElementById("analyticsChart");
  if (!colElem || !typeElem || !canvas) return;

  if (!currentDataset || !currentDataset.rows || currentDataset.rows.length === 0) {
    if (activeChart) { activeChart.destroy(); activeChart = null; }
    return;
  }

  const col = colElem.value;
  const chartType = typeElem.value;
  if (!col) return;

  // Extract column values from rows
  const rawValues = currentDataset.rows.map(r => r[col]).filter(v => v !== null && v !== undefined && v !== "" && v !== "NaN");
  const isNumeric = isColumnNumeric(col, currentDataset.metrics);

  let chartLabels = [];
  let chartData = [];

  if (isNumeric && chartType === "histogram" && rawValues.length > 0) {
    // Compute 8 histogram bins
    const numbers = rawValues.map(v => Number(v)).filter(n => !isNaN(n));
    if (numbers.length > 0) {
      const min = Math.min(...numbers);
      const max = Math.max(...numbers);
      const binCount = Math.min(8, Math.max(3, Math.floor(numbers.length / 2)));
      const step = (max - min) / (binCount || 1);

      const bins = new Array(binCount).fill(0);
      const binLabels = [];

      for (let i = 0; i < binCount; i++) {
        const bStart = min + i * step;
        const bEnd = i === binCount - 1 ? max : min + (i + 1) * step;
        binLabels.push(`${bStart.toFixed(1)}–${bEnd.toFixed(1)}`);
      }

      numbers.forEach(num => {
        let bIdx = Math.floor((num - min) / (step || 1));
        if (bIdx >= binCount) bIdx = binCount - 1;
        if (bIdx < 0) bIdx = 0;
        bins[bIdx]++;
      });

      chartLabels = binLabels;
      chartData = bins;
    }
  } else {
    // Categorical frequency counts (Top 12)
    const freq = {};
    rawValues.forEach(v => {
      const k = String(v).trim();
      freq[k] = (freq[k] || 0) + 1;
    });

    const sortedEntries = Object.entries(freq).sort((a, b) => b[1] - a[1]).slice(0, 12);
    chartLabels = sortedEntries.map(e => e[0]);
    chartData = sortedEntries.map(e => e[1]);
  }

  const ctx = canvas.getContext("2d");
  if (activeChart) {
    activeChart.destroy();
  }

  activeChart = new Chart(ctx, {
    type: "bar",
    data: {
      labels: chartLabels,
      datasets: [{
        label: col.trim(),
        data: chartData,
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
          text: `Distribution of ${col.trim()} (${isNumeric ? 'Histogram' : 'Frequency Counts'})`,
          font: { size: 14, weight: "bold" },
          color: "#161616"
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          grid: { color: "#F3F4F6" },
          ticks: { color: "#666", precision: 0 }
        },
        x: {
          grid: { display: false },
          ticks: { color: "#666" }
        }
      }
    }
  });
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

function openTeamModal() {
  openModal("teamModal");
}

function openMissingModal() {
  if (!currentDataset || !currentDataset.has_data) {
    showToast("Please select or load a CSV dataset first.");
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
  if (group) group.style.display = strat === "custom" ? "flex" : "none";
}

function applyMissingStrategy() {
  const col = document.getElementById("missingCol").value;
  const strategy = document.getElementById("missingStrategy").value;
  const customVal = document.getElementById("customValInput")?.value;

  closeModal("missingModal");
  triggerClean("handle_missing", { column: col, strategy, custom_val: customVal });
}

function openDropColModal() {
  if (!currentDataset || !currentDataset.has_data) {
    showToast("Please select or load a CSV dataset first.");
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
    showToast("Please select or load a CSV dataset first.");
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
  if (str === null || str === undefined) return "";
  return String(str).replace(/[&<>"']/g, m => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[m]);
}

function escapeAttribute(str) {
  if (str === null || str === undefined) return "";
  return String(str).replace(/'/g, "\\'").replace(/"/g, '&quot;');
}
