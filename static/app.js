let activeChart = null;
let currentDataset = null;

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

  const m = data.metrics;
  const dupTag = document.getElementById("dupCountTag");
  const nullTag = document.getElementById("nullCountTag");

  dupTag.innerText = m.duplicate_count > 0 ? `${m.duplicate_count} duplicate rows` : "0 duplicates";
  dupTag.className = m.duplicate_count > 0 ? "tag red" : "tag green";

  nullTag.innerText = m.total_missing_cells > 0 ? `${m.total_missing_cells} missing cells` : "0 missing cells";
  nullTag.className = m.total_missing_cells > 0 ? "tag red" : "tag green";

  document.getElementById("dockStatusText").innerText =
    m.duplicate_count === 0 && m.total_missing_cells === 0
      ? "Dataset is 100% clean and ready for export."
      : "Data issues detected. Click 'Auto-Clean CSV' or select individual tools above.";

  renderTable(data.columns, data.rows);
  document.getElementById("auditViewer").innerText = data.report_text || "No cleaning actions performed yet.";

  populateColumnDropdowns(data.columns);
  updateStats();
  updateChart();
}

function renderTable(columns, rows) {
  const container = document.getElementById("tableContainer");
  if (!rows || rows.length === 0) {
    container.innerHTML = '<div style="padding: 24px; text-align: center; color: #888;">The loaded dataset is empty.</div>';
    return;
  }

  let html = '<table><thead><tr>';
  html += '<th class="row-index">#</th>';
  columns.forEach(col => {
    html += `<th>${escapeHtml(col)}</th>`;
  });
  html += '</tr></thead><tbody>';

  rows.forEach((row, idx) => {
    html += '<tr>';
    html += `<td class="row-index">${idx + 1}</td>`;
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

function populateColumnDropdowns(columns) {
  const chartCol = document.getElementById("chartColumn");
  const missingCol = document.getElementById("missingCol");

  const prevChartVal = chartCol.value;
  chartCol.innerHTML = "";
  columns.forEach(col => {
    const opt = document.createElement("option");
    opt.value = col;
    opt.innerText = col;
    chartCol.appendChild(opt);
  });

  if (columns.includes(prevChartVal)) {
    chartCol.value = prevChartVal;
  }

  missingCol.innerHTML = '<option value="all">All Columns</option>';
  columns.forEach(col => {
    const opt = document.createElement("option");
    opt.value = col;
    opt.innerText = col;
    missingCol.appendChild(opt);
  });
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
  const col = document.getElementById("chartColumn").value;
  const chartType = document.getElementById("chartType").value;
  if (!col) return;

  try {
    const res = await fetch(`/api/chart-data?column=${encodeURIComponent(col)}&type=${chartType}`);
    const data = await res.json();

    const ctx = document.getElementById("analyticsChart").getContext("2d");
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

function openMissingModal() {
  if (!currentDataset || !currentDataset.has_data) {
    showToast("Please select a CSV file first.");
    return;
  }
  document.getElementById("missingModal").style.display = "flex";
}

function closeMissingModal() {
  document.getElementById("missingModal").style.display = "none";
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

  closeMissingModal();
  triggerClean("handle_missing", { column: col, strategy, custom_val: customVal });
}

function showToast(msg) {
  const toast = document.getElementById("toastNotification");
  toast.innerText = msg;
  toast.classList.add("show");
  setTimeout(() => toast.classList.remove("show"), 2800);
}

function escapeHtml(str) {
  if (typeof str !== "string") return str;
  return str.replace(/[&<>"']/g, m => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[m]);
}
