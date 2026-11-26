let activeChart = null;
let currentDataset = null;

document.addEventListener("DOMContentLoaded", () => {
  fetchState();
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

  const fileBadge = document.getElementById("fileBadge");
  const shapeBadge = document.getElementById("shapeBadge");
  const dupBadge = document.getElementById("dupBadge");
  const nullBadge = document.getElementById("nullBadge");
  const headerBadge = document.getElementById("headerBadge");

  const dupPill = document.getElementById("dupPill");
  const nullPill = document.getElementById("nullPill");
  const headerPill = document.getElementById("headerPill");

  if (!data.has_data) {
    fileBadge.innerText = "None Loaded";
    shapeBadge.innerText = "0 rows × 0 cols";
    dupBadge.innerText = "0";
    nullBadge.innerText = "0";
    headerBadge.innerText = "Standard";

    dupPill.className = "status-pill status-clean";
    dupPill.innerText = "No Duplicates";
    nullPill.className = "status-pill status-clean";
    nullPill.innerText = "Zero Missing";
    headerPill.className = "status-pill status-clean";
    headerPill.innerText = "Clean";

    document.getElementById("tableContainer").innerHTML = `
      <div class="empty-state">
        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
        <p>No dataset loaded. Select <strong>Students Sample</strong> or upload a CSV file.</p>
      </div>`;
    document.getElementById("auditViewer").innerText = "Awaiting dataset operations.";
    return;
  }

  fileBadge.innerText = data.filename || "Uploaded File";
  shapeBadge.innerText = `${data.total_rows} rows × ${data.columns.length} cols`;

  const m = data.metrics;

  dupBadge.innerText = m.duplicate_count;
  if (m.duplicate_count > 0) {
    dupPill.className = "status-pill status-dirty";
    dupPill.innerText = `${m.duplicate_count} Repeats`;
  } else {
    dupPill.className = "status-pill status-clean";
    dupPill.innerText = "No Duplicates";
  }

  nullBadge.innerText = m.total_missing_cells;
  if (m.total_missing_cells > 0) {
    nullPill.className = "status-pill status-dirty";
    nullPill.innerText = `${m.total_missing_cells} Missing`;
  } else {
    nullPill.className = "status-pill status-clean";
    nullPill.innerText = "Zero Missing";
  }

  if (m.has_unclean_headers) {
    headerBadge.innerText = "Irregular";
    headerPill.className = "status-pill status-warning";
    headerPill.innerText = "Needs Format";
  } else {
    headerBadge.innerText = "Standard";
    headerPill.className = "status-pill status-clean";
    headerPill.innerText = "Clean";
  }

  renderTable(data.columns, data.rows);
  document.getElementById("auditViewer").innerText = data.report_text || "No actions logged.";

  populateColumnDropdowns(data.columns);
  updateStats();
  updateChart();
}

function renderTable(columns, rows) {
  const container = document.getElementById("tableContainer");
  if (!rows || rows.length === 0) {
    container.innerHTML = '<div class="empty-state"><p>The loaded dataset is empty.</p></div>';
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

async function loadSample(sampleName) {
  showToast(`Loading ${sampleName} dataset...`);
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
  event.target.value = "";
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
      showToast(result.message);
    } else {
      showToast(result.message);
    }
  } catch (err) {
    showToast("Reset failed.");
  }
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
    container.innerHTML = '<div class="empty-state"><p>Load a dataset to view descriptive statistics.</p></div>';
    return;
  }

  try {
    const res = await fetch("/api/stats");
    const data = await res.json();

    let html = '<div style="display:flex; flex-direction:column; gap:20px;">';

    if (data.numeric && Object.keys(data.numeric).length > 0) {
      html += '<div><h4 style="margin-bottom:8px; font-size:13px; font-weight:600; color:#9CA3AF; text-transform:uppercase; letter-spacing:0.04em;">Five-Number Numerical Summary</h4>';
      html += '<div class="table-container"><table><thead><tr><th>Metric</th>';
      const cols = Object.keys(data.numeric);
      cols.forEach(c => html += `<th>${escapeHtml(c)}</th>`);
      html += '</tr></thead><tbody>';

      const metrics = ["count", "mean", "std", "min", "25%", "50%", "75%", "max"];
      metrics.forEach(m => {
        html += `<tr><td><strong style="color: #60A5FA;">${m}</strong></td>`;
        cols.forEach(c => {
          const val = data.numeric[c][m];
          html += `<td>${val !== undefined ? val : "-"}</td>`;
        });
        html += '</tr>';
      });
      html += '</tbody></table></div></div>';
    }

    if (data.categorical && Object.keys(data.categorical).length > 0) {
      html += '<div><h4 style="margin-bottom:8px; font-size:13px; font-weight:600; color:#9CA3AF; text-transform:uppercase; letter-spacing:0.04em;">Categorical Distributions</h4>';
      for (const [col, rows] of Object.entries(data.categorical)) {
        html += `<div style="margin-bottom: 14px;"><h5 style="margin-bottom:6px; font-size:12px; color:#D1D5DB;">Column: <strong style="color:#F3F4F6;">${escapeHtml(col)}</strong></h5>`;
        html += '<div class="table-container" style="max-height: 180px;"><table><thead><tr><th>Category</th><th>Count</th><th>Percentage</th></tr></thead><tbody>';
        rows.forEach(r => {
          html += `<tr><td>${escapeHtml(r.category)}</td><td>${r.count}</td><td><span style="color:#34D399; font-weight:600;">${r.percentage}%</span></td></tr>`;
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
          backgroundColor: "#3B82F6",
          borderColor: "#60A5FA",
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
            font: { size: 13, weight: "bold", family: "'Inter', sans-serif" },
            color: "#F3F4F6"
          },
          tooltip: {
            backgroundColor: "#1F2937",
            borderColor: "#374151",
            borderWidth: 1,
            titleColor: "#93C5FD",
            bodyColor: "#F3F4F6"
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            grid: { color: "#1F2937" },
            ticks: { color: "#9CA3AF" }
          },
          x: {
            grid: { display: false },
            ticks: { color: "#9CA3AF" }
          }
        }
      }
    });
  } catch (err) {
    console.error("Error updating chart:", err);
  }
}

function switchTab(tabId, el) {
  document.querySelectorAll(".tab-item").forEach(btn => btn.classList.remove("active"));
  document.querySelectorAll(".tab-pane").forEach(c => c.style.display = "none");

  if (el) {
    el.classList.add("active");
  }
  const target = document.getElementById(tabId);
  if (target) {
    target.style.display = "block";
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
  const toast = document.getElementById("toast");
  toast.innerText = msg;
  toast.classList.add("show");
  setTimeout(() => toast.classList.remove("show"), 2800);
}

function escapeHtml(str) {
  if (typeof str !== "string") return str;
  return str.replace(/[&<>"']/g, m => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[m]);
}
