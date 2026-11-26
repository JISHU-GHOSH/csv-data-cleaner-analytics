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

  if (!data.has_data) {
    fileBadge.innerText = "None loaded";
    shapeBadge.innerText = "0 rows × 0 cols";
    dupBadge.innerText = "0";
    dupBadge.className = "badge";
    nullBadge.innerText = "0";
    nullBadge.className = "badge";
    headerBadge.innerText = "Clean";
    headerBadge.className = "badge";

    document.getElementById("tableContainer").innerHTML = '<div class="empty-state">No dataset loaded. Click a sample above or upload a CSV file.</div>';
    document.getElementById("auditViewer").innerText = "No actions performed yet.";
    return;
  }

  fileBadge.innerText = data.filename || "Uploaded File";
  shapeBadge.innerText = `${data.total_rows} rows × ${data.columns.length} cols`;

  const m = data.metrics;
  dupBadge.innerText = m.duplicate_count;
  dupBadge.className = m.duplicate_count > 0 ? "badge badge-danger" : "badge badge-clean";

  nullBadge.innerText = m.total_missing_cells;
  nullBadge.className = m.total_missing_cells > 0 ? "badge badge-danger" : "badge badge-clean";

  headerBadge.innerText = m.has_unclean_headers ? "Irregular" : "Clean";
  headerBadge.className = m.has_unclean_headers ? "badge badge-warning" : "badge badge-clean";

  renderTable(data.columns, data.rows);
  document.getElementById("auditViewer").innerText = data.report_text || "No actions logged.";

  populateColumnDropdowns(data.columns);
  updateStats();
  updateChart();
}

function renderTable(columns, rows) {
  const container = document.getElementById("tableContainer");
  if (!rows || rows.length === 0) {
    container.innerHTML = '<div class="empty-state">Dataset is empty.</div>';
    return;
  }

  let html = '<table><thead><tr>';
  columns.forEach(col => {
    html += `<th>${escapeHtml(col)}</th>`;
  });
  html += '</tr></thead><tbody>';

  rows.forEach(row => {
    html += '<tr>';
    columns.forEach(col => {
      const val = row[col];
      if (val === null || val === undefined) {
        html += '<td><span class="nan-cell">&lt;NaN&gt;</span></td>';
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
    showToast("Error loading sample.");
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
      showToast(result.message);
    } else {
      showToast(result.message);
    }
  } catch (err) {
    showToast("Error uploading file.");
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
      showToast(result.message);
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
    container.innerHTML = '<div class="empty-state">Load a dataset to view descriptive statistics.</div>';
    return;
  }

  try {
    const res = await fetch("/api/stats");
    const data = await res.json();

    let html = '<div style="display:flex; flex-direction:column; gap:1.5rem;">';

    if (data.numeric && Object.keys(data.numeric).length > 0) {
      html += '<div><h4 style="margin-bottom:0.6rem; color:#1e293b;">Numeric Summary (Five-Number Metrics)</h4><div class="table-container"><table><thead><tr><th>Metric</th>';
      const cols = Object.keys(data.numeric);
      cols.forEach(c => html += `<th>${escapeHtml(c)}</th>`);
      html += '</tr></thead><tbody>';

      const metrics = ["count", "mean", "std", "min", "25%", "50%", "75%", "max"];
      metrics.forEach(m => {
        html += `<tr><td><strong>${m}</strong></td>`;
        cols.forEach(c => {
          html += `<td>${data.numeric[c][m] !== undefined ? data.numeric[c][m] : "-"}</td>`;
        });
        html += '</tr>';
      });
      html += '</tbody></table></div></div>';
    }

    if (data.categorical && Object.keys(data.categorical).length > 0) {
      html += '<div><h4 style="margin-bottom:0.6rem; color:#1e293b;">Categorical Distributions</h4>';
      for (const [col, rows] of Object.entries(data.categorical)) {
        html += `<h5 style="margin: 0.8rem 0 0.4rem 0; color:#475569;">${escapeHtml(col)}</h5><div class="table-container"><table><thead><tr><th>Category</th><th>Count</th><th>Percentage</th></tr></thead><tbody>`;
        rows.forEach(r => {
          html += `<tr><td>${escapeHtml(r.category)}</td><td>${r.count}</td><td>${r.percentage}%</td></tr>`;
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
          label: `${col} Distribution`,
          data: data.values,
          backgroundColor: "rgba(37, 99, 235, 0.7)",
          borderColor: "rgba(37, 99, 235, 1)",
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
            font: { size: 14, weight: "bold" }
          }
        },
        scales: {
          y: { beginAtZero: true, grid: { color: "#f1f5f9" } },
          x: { grid: { display: false } }
        }
      }
    });
  } catch (err) {
    console.error("Error updating chart", err);
  }
}

function switchTab(tabId) {
  document.querySelectorAll(".tab-btn").forEach(btn => btn.classList.remove("active"));
  document.querySelectorAll(".tab-content").forEach(c => c.style.display = "none");

  event.target.classList.add("active");
  document.getElementById(tabId).style.display = "flex";

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
  setTimeout(() => toast.classList.remove("show"), 3000);
}

function escapeHtml(str) {
  if (typeof str !== "string") return str;
  return str.replace(/[&<>"']/g, m => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[m]);
}
