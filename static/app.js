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

  if (!data.has_data) {
    fileBadge.innerText = "None";
    shapeBadge.innerText = "0 rows × 0 cols";
    dupBadge.innerText = "0";
    dupBadge.className = "value tag";
    nullBadge.innerText = "0";
    nullBadge.className = "value tag";
    headerBadge.innerText = "Normal";
    headerBadge.className = "value tag";

    document.getElementById("tableContainer").innerHTML = '<div class="empty-state"><p>No dataset loaded. Click <strong>"Sample: Students"</strong> above or open a local CSV file.</p></div>';
    document.getElementById("auditViewer").innerText = "No cleaning operations performed yet.";
    return;
  }

  fileBadge.innerText = data.filename || "Uploaded File";
  shapeBadge.innerText = `${data.total_rows} rows × ${data.columns.length} cols`;

  const m = data.metrics;

  dupBadge.innerText = m.duplicate_count;
  dupBadge.className = m.duplicate_count > 0 ? "value tag danger" : "value tag";

  nullBadge.innerText = m.total_missing_cells;
  nullBadge.className = m.total_missing_cells > 0 ? "value tag danger" : "value tag";

  if (m.has_unclean_headers) {
    headerBadge.innerText = "Needs Format";
    headerBadge.className = "value tag warning";
  } else {
    headerBadge.innerText = "Standardized";
    headerBadge.className = "value tag";
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
  html += '<th class="row-num">#</th>';
  columns.forEach(col => {
    html += `<th>${escapeHtml(col)}</th>`;
  });
  html += '</tr></thead><tbody>';

  rows.forEach((row, idx) => {
    html += '<tr>';
    html += `<td class="row-num">${idx + 1}</td>`;
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
      html += '<div><h4 style="margin-bottom:8px; font-size:13px; font-weight:600; color:#1f2328;">Five-Number Numerical Summary</h4>';
      html += '<div class="table-wrap"><table><thead><tr><th>Metric</th>';
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
      html += '<div><h4 style="margin-bottom:8px; font-size:13px; font-weight:600; color:#1f2328;">Categorical Distributions</h4>';
      for (const [col, rows] of Object.entries(data.categorical)) {
        html += `<div style="margin-bottom: 12px;"><h5 style="margin-bottom:4px; font-size:12px; color:#656d76;">Column: <strong>${escapeHtml(col)}</strong></h5>`;
        html += '<div class="table-wrap" style="max-height: 180px;"><table><thead><tr><th>Category</th><th>Count</th><th>Percentage</th></tr></thead><tbody>';
        rows.forEach(r => {
          html += `<tr><td>${escapeHtml(r.category)}</td><td>${r.count}</td><td>${r.percentage}%</td></tr>`;
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
          backgroundColor: "#0969da",
          borderColor: "#0969da",
          borderWidth: 1,
          borderRadius: 2
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
            font: { size: 13, weight: "bold" },
            color: "#1f2328"
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            grid: { color: "#eaeef2" },
            ticks: { color: "#656d76" }
          },
          x: {
            grid: { display: false },
            ticks: { color: "#656d76" }
          }
        }
      }
    });
  } catch (err) {
    console.error("Error updating chart:", err);
  }
}

function switchTab(tabId, el) {
  document.querySelectorAll(".tab-btn").forEach(btn => btn.classList.remove("active"));
  document.querySelectorAll(".tab-content").forEach(c => c.style.display = "none");

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
