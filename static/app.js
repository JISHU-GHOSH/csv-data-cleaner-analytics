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
    console.error("Failed to load initial state", err);
  }
}

function renderState(data) {
  currentDataset = data;

  const fileBadge = document.getElementById("fileBadge");
  const shapeBadge = document.getElementById("shapeBadge");
  const dupBadge = document.getElementById("dupBadge");
  const nullBadge = document.getElementById("nullBadge");
  const headerBadge = document.getElementById("headerBadge");

  const dupCard = document.getElementById("dupCard");
  const nullCard = document.getElementById("nullCard");
  const headerCard = document.getElementById("headerCard");

  const dupPill = document.getElementById("dupPill");
  const nullPill = document.getElementById("nullPill");
  const headerPill = document.getElementById("headerPill");

  if (!data.has_data) {
    fileBadge.innerText = "No dataset loaded";
    shapeBadge.innerText = "0 rows × 0 columns";
    dupBadge.innerText = "0";
    nullBadge.innerText = "0";
    headerBadge.innerText = "Standardized";

    dupCard.className = "kpi-card";
    nullCard.className = "kpi-card";
    headerCard.className = "kpi-card";

    dupPill.className = "kpi-status-pill clean";
    dupPill.innerText = "Clean";
    nullPill.className = "kpi-status-pill clean";
    nullPill.innerText = "Complete";
    headerPill.className = "kpi-status-pill clean";
    headerPill.innerText = "Optimized";

    renderDropzone();
    document.getElementById("auditViewer").innerText = "Ready. Awaiting dataset operations.";
    return;
  }

  fileBadge.innerText = data.filename || "Uploaded File";
  shapeBadge.innerText = `${data.total_rows} rows × ${data.columns.length} columns`;

  const m = data.metrics;

  dupBadge.innerText = m.duplicate_count;
  if (m.duplicate_count > 0) {
    dupCard.className = "kpi-card dirty";
    dupPill.className = "kpi-status-pill dirty";
    dupPill.innerText = `${m.duplicate_count} Repeats`;
  } else {
    dupCard.className = "kpi-card clean";
    dupPill.className = "kpi-status-pill clean";
    dupPill.innerText = "Clean";
  }

  nullBadge.innerText = m.total_missing_cells;
  if (m.total_missing_cells > 0) {
    nullCard.className = "kpi-card dirty";
    nullPill.className = "kpi-status-pill dirty";
    nullPill.innerText = `${m.total_missing_cells} Nulls`;
  } else {
    nullCard.className = "kpi-card clean";
    nullPill.className = "kpi-status-pill clean";
    nullPill.innerText = "100% Filled";
  }

  if (m.has_unclean_headers) {
    headerBadge.innerText = "Irregular";
    headerCard.className = "kpi-card dirty";
    headerPill.className = "kpi-status-pill warning";
    headerPill.innerText = "Fix Needed";
  } else {
    headerBadge.innerText = "Standardized";
    headerCard.className = "kpi-card clean";
    headerPill.className = "kpi-status-pill clean";
    headerPill.innerText = "Optimized";
  }

  renderTable(data.columns, data.rows);
  document.getElementById("auditViewer").innerText = data.report_text || "No actions logged.";

  populateColumnDropdowns(data.columns);
  updateStats();
  updateChart();
}

function renderDropzone() {
  const container = document.getElementById("tableContainer");
  container.innerHTML = `
    <div class="empty-dropzone" onclick="document.getElementById('fileInput').click()">
      <div class="dropzone-icon">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
      </div>
      <h3>Drag and drop your raw CSV file here</h3>
      <p>or click to browse files from your computer</p>
      <div class="demo-suggestions">
        <span>or try:</span>
        <button type="button" class="chip-link" onclick="event.stopPropagation(); loadSample('students')">🎓 Students Demo</button>
        <button type="button" class="chip-link" onclick="event.stopPropagation(); loadSample('sales')">💼 Sales Demo</button>
      </div>
    </div>
  `;
}

function renderTable(columns, rows) {
  const container = document.getElementById("tableContainer");
  if (!rows || rows.length === 0) {
    container.innerHTML = '<div class="empty-state" style="padding: 3rem; text-align: center; color: var(--text-muted);">Dataset is empty.</div>';
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

  missingCol.innerHTML = '<option value="all">All Columns (Global)</option>';
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
      showToast(`Loaded ${sampleName} dataset with deliberate flaws.`);
    } else {
      showToast(result.message);
    }
  } catch (err) {
    showToast("Error loading sample.");
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
    showToast("Error uploading file.");
  }
}

async function triggerClean(action, params = {}) {
  showToast("Applying transformation...");
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
    showToast("Failed to clean dataset.");
  }
}

async function resetData() {
  showToast("Restoring to raw state...");
  try {
    const res = await fetch("/api/reset", { method: "POST" });
    const result = await res.json();
    if (result.success) {
      renderState(result.data);
      showToast("Dataset restored to initial state.");
    } else {
      showToast(result.message);
    }
  } catch (err) {
    showToast("Failed to reset dataset.");
  }
}

function downloadCleanCSV() {
  window.location.href = "/api/export/csv";
}

function downloadReport() {
  window.location.href = "/api/export/report";
}

async function updateStats() {
  const container = document.getElementById("statsContainer");
  if (!currentDataset || !currentDataset.has_data) {
    container.innerHTML = '<div class="empty-state" style="padding: 3rem; text-align: center; color: var(--text-muted);">Load a dataset to view descriptive statistics.</div>';
    return;
  }

  try {
    const res = await fetch("/api/stats");
    const data = await res.json();

    let html = '<div class="stats-wrapper">';

    if (data.numeric && Object.keys(data.numeric).length > 0) {
      html += '<div><div class="stats-card-title"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 20V10M12 20V4M6 20v-6"/></svg> Five-Number Numerical Summary</div>';
      html += '<div class="table-frame"><table><thead><tr><th>Metric</th>';
      const cols = Object.keys(data.numeric);
      cols.forEach(c => html += `<th>${escapeHtml(c)}</th>`);
      html += '</tr></thead><tbody>';

      const metrics = ["count", "mean", "std", "min", "25%", "50%", "75%", "max"];
      metrics.forEach(m => {
        html += `<tr><td><strong style="color: #38BDF8;">${m}</strong></td>`;
        cols.forEach(c => {
          const val = data.numeric[c][m];
          html += `<td>${val !== undefined ? val : "-"}</td>`;
        });
        html += '</tr>';
      });
      html += '</tbody></table></div></div>';
    }

    if (data.categorical && Object.keys(data.categorical).length > 0) {
      html += '<div><div class="stats-card-title"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg> Categorical Frequency Distributions</div>';
      for (const [col, rows] of Object.entries(data.categorical)) {
        html += `<h5 style="margin: 0.9rem 0 0.5rem; color: #94A3B8; font-size: 0.85rem;">Column: <span style="color: #F8FAFC;">${escapeHtml(col)}</span></h5>`;
        html += '<div class="table-frame" style="max-height: 220px;"><table><thead><tr><th>Category</th><th>Count</th><th>Distribution (%)</th></tr></thead><tbody>';
        rows.forEach(r => {
          html += `<tr><td>${escapeHtml(r.category)}</td><td>${r.count}</td><td><span style="color: #34D399; font-weight: 600;">${r.percentage}%</span></td></tr>`;
        });
        html += '</tbody></table></div>';
      }
      html += '</div>';
    }

    html += '</div>';
    container.innerHTML = html;
  } catch (err) {
    console.error("Error updating stats", err);
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
          label: `${col}`,
          data: data.values,
          backgroundColor: "rgba(99, 102, 241, 0.75)",
          hoverBackgroundColor: "rgba(129, 140, 248, 1)",
          borderColor: "rgba(165, 180, 252, 0.9)",
          borderWidth: 1,
          borderRadius: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          title: {
            display: true,
            text: `Distribution Spread: ${col}`,
            color: "#F8FAFC",
            font: { size: 14, weight: "bold", family: "'Plus Jakarta Sans', sans-serif" }
          },
          tooltip: {
            backgroundColor: "#0F172A",
            titleColor: "#38BDF8",
            bodyColor: "#F8FAFC",
            borderColor: "#334155",
            borderWidth: 1,
            padding: 10,
            cornerRadius: 8
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            grid: { color: "rgba(51, 65, 85, 0.3)" },
            ticks: { color: "#94A3B8", font: { family: "'JetBrains Mono', monospace" } }
          },
          x: {
            grid: { display: false },
            ticks: { color: "#94A3B8", font: { family: "'Plus Jakarta Sans', sans-serif" } }
          }
        }
      }
    });
  } catch (err) {
    console.error("Error updating chart", err);
  }
}

function switchTab(tabId, el) {
  document.querySelectorAll(".studio-tab").forEach(btn => btn.classList.remove("active"));
  document.querySelectorAll(".tab-pane").forEach(c => c.classList.remove("active"));

  if (el) {
    el.classList.add("active");
  }
  const target = document.getElementById(tabId);
  if (target) {
    target.classList.add("active");
  }

  if (tabId === "chartTab") {
    setTimeout(updateChart, 50);
  }
}

function openMissingModal() {
  if (!currentDataset || !currentDataset.has_data) {
    showToast("Please load a dataset first.");
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
  setTimeout(() => toast.classList.remove("show"), 3200);
}

function escapeHtml(str) {
  if (typeof str !== "string") return str;
  return str.replace(/[&<>"']/g, m => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[m]);
}
