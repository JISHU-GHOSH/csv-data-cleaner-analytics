import os
import io
import json
import uuid
import webbrowser
import threading
from typing import Tuple, Dict
from flask import Flask, render_template, request, jsonify, send_file, session
import pandas as pd
import numpy as np

from core.data_manager import DataManager
from core.audit_logger import AuditLogger
from core.exporter import save_csv, save_report
import core.cleaner as cleaner
import core.stats_engine as stats_engine

app = Flask(__name__)
app.config["SECRET_KEY"] = "csv-cleaner-secret-key-2026-rocket"

# Session-isolated memory storage for state management
session_stores: Dict[str, Dict[str, any]] = {}

def get_session_context() -> Tuple[str, DataManager, AuditLogger]:
    """Retrieve or create an isolated session DataManager and AuditLogger."""
    # Check header first (sent by fetch in app.js), then cookie session
    sid = request.headers.get("X-Session-ID") or session.get("session_id")
    if not sid:
        sid = str(uuid.uuid4())
        session["session_id"] = sid

    if sid not in session_stores:
        session_stores[sid] = {
            "mgr": DataManager(),
            "logger": AuditLogger()
        }

    # Evict oldest sessions if memory exceeds 200 sessions
    if len(session_stores) > 200:
        oldest_key = next(iter(session_stores))
        del session_stores[oldest_key]

    return sid, session_stores[sid]["mgr"], session_stores[sid]["logger"]

def build_state_response(data_mgr: DataManager, logger: AuditLogger, sid: str) -> dict:
    if not data_mgr.has_data():
        return {
            "session_id": sid,
            "has_data": False,
            "filename": "",
            "metrics": {},
            "columns": [],
            "rows": [],
            "total_rows": 0,
            "audit_logs": [],
            "report_text": "",
        }

    df = data_mgr.current_df
    metrics = data_mgr.get_health_metrics()
    display_df = df.head(300)

    rows = []
    for _, r in display_df.iterrows():
        row_dict = {}
        for col in df.columns:
            val = r[col]
            row_dict[col] = None if pd.isna(val) else str(val)
        rows.append(row_dict)

    return {
        "session_id": sid,
        "has_data": True,
        "filename": data_mgr.source_name,
        "metrics": metrics,
        "columns": list(df.columns),
        "rows": rows,
        "total_rows": len(df),
        "audit_logs": logger.get_logs(),
        "report_text": logger.get_report_text(),
    }

@app.route("/")
def index():
    return render_template("index.html")

# Academic Deliverable Viewer & Download Routes
@app.route("/docs/report")
def view_report_html():
    report_path = os.path.join(os.path.dirname(__file__), "MAJOR_PROJECT_REPORT.html")
    if os.path.exists(report_path):
        return send_file(report_path, mimetype="text/html")
    return "Report not generated yet.", 404

@app.route("/docs/paper")
def view_paper_html():
    paper_path = os.path.join(os.path.dirname(__file__), "RESEARCH_PAPER.html")
    if os.path.exists(paper_path):
        return send_file(paper_path, mimetype="text/html")
    return "Research paper not generated yet.", 404

@app.route("/download/report-docx")
def download_report_docx():
    path = os.path.join(os.path.dirname(__file__), "MAJOR_PROJECT_REPORT.docx")
    if os.path.exists(path):
        return send_file(path, as_attachment=True, download_name="MAJOR_PROJECT_REPORT_TEAM_ROCKET.docx")
    return "Document not found.", 404

@app.route("/download/paper-docx")
def download_paper_docx():
    path = os.path.join(os.path.dirname(__file__), "RESEARCH_PAPER.docx")
    if os.path.exists(path):
        return send_file(path, as_attachment=True, download_name="RESEARCH_PAPER_IEEE_TEAM_ROCKET.docx")
    return "Document not found.", 404

@app.route("/download/presentation-pptx")
def download_presentation_pptx():
    path = os.path.join(os.path.dirname(__file__), "CSV_Cleaner_Major_Project_Presentation.pptx")
    if not os.path.exists(path):
        path = os.path.join(os.path.dirname(__file__), "CSV_Cleaner_14_Pages_Presentation.pptx")
    if os.path.exists(path):
        return send_file(path, as_attachment=True, download_name="PROJECT_PRESENTATION_TEAM_ROCKET.pptx")
    return "Presentation not found.", 404

@app.route("/api/project-info", methods=["GET"])
def get_project_info():
    return jsonify({
        "project_title": "CSV Data Cleaner & Analytics Studio",
        "short_title": "CSVCleaner Studio",
        "team_name": "ROCKET",
        "institution": "JECRC University, Jaipur",
        "department": "Department of Computer Science & Engineering",
        "degree": "Bachelor of Technology (B.Tech)",
        "session": "2025–2026",
        "supervisor": "Dr./Mr./Ms. XYZ, Assistant Professor, Dept. of CSE",
        "members": [
            {"name": "Parth Kothari", "id": "25BCON0044", "role": "Project Report File & Documentation Lead"},
            {"name": "Hardik Udawat", "id": "25BCON0081", "role": "Project Presentation (PPT) & Delivery Lead"},
            {"name": "Twisha Srivastava", "id": "25BCON0266", "role": "Research Paper & Empirical Methodology Lead"},
            {"name": "Jishu Ghosh", "id": "25BCON0022", "role": "Software Architecture, Development & Deployment Lead"}
        ]
    })

@app.route("/api/state", methods=["GET"])
def get_state_route():
    sid, data_mgr, logger = get_session_context()
    return jsonify(build_state_response(data_mgr, logger, sid))

@app.route("/api/load-sample", methods=["POST"])
def load_sample():
    sid, data_mgr, logger = get_session_context()
    payload = request.json or {}
    key = payload.get("sample", "students")
    success, msg = data_mgr.load_sample(key)
    if success:
        logger.clear()
        name = "Students Dataset (Dirty)" if key == "students" else "Sales Dataset (Dirty)"
        logger.log("Sample Loaded", f"Loaded bundled sample: {name}")
        return jsonify({"success": True, "message": msg, "data": build_state_response(data_mgr, logger, sid)})
    return jsonify({"success": False, "message": msg}), 400

@app.route("/api/upload", methods=["POST"])
def upload_file():
    sid, data_mgr, logger = get_session_context()
    if "file" not in request.files:
        return jsonify({"success": False, "message": "No file uploaded."}), 400

    file = request.files["file"]
    if not file.filename.endswith(".csv"):
        return jsonify({"success": False, "message": "Only CSV files are supported."}), 400

    try:
        df = pd.read_csv(file)
        if df.empty:
            return jsonify({"success": False, "message": "Uploaded CSV file is empty."}), 400

        data_mgr.raw_df = df.copy(deep=True)
        data_mgr.current_df = df.copy(deep=True)
        data_mgr.source_name = file.filename
        data_mgr.history.clear()
        logger.clear()
        logger.log("File Uploaded", f"Uploaded '{file.filename}'")
        return jsonify({"success": True, "message": f"Uploaded {file.filename} successfully.", "data": build_state_response(data_mgr, logger, sid)})
    except Exception as e:
        return jsonify({"success": False, "message": f"Failed to parse CSV: {str(e)}"}), 400

@app.route("/api/clean", methods=["POST"])
def clean_action():
    sid, data_mgr, logger = get_session_context()
    payload = request.json or {}

    # State re-hydration defense for serverless environment
    if not data_mgr.has_data() and payload.get("current_csv"):
        try:
            df = pd.read_csv(io.StringIO(payload["current_csv"]))
            data_mgr.current_df = df
            data_mgr.source_name = payload.get("source_name", "dataset.csv")
        except Exception:
            pass

    if not data_mgr.has_data():
        return jsonify({"success": False, "message": "No dataset loaded. Please upload or select a CSV."}), 400

    action = payload.get("action")
    data_mgr.push_history()

    if action == "auto_clean":
        clean_df, logs = cleaner.auto_clean_all(data_mgr.current_df)
        data_mgr.current_df = clean_df
        for l in logs:
            logger.log("Auto-Clean", l)
        msg = f"Auto-clean completed: applied {len(logs)} automated cleaning steps."

    elif action == "standardize_headers":
        df, msg = cleaner.standardize_headers(data_mgr.current_df)
        data_mgr.current_df = df
        logger.log("Standardize Headers", msg)

    elif action == "remove_duplicates":
        df, msg, _ = cleaner.remove_duplicates(data_mgr.current_df)
        data_mgr.current_df = df
        logger.log("Remove Duplicates", msg)

    elif action == "trim_whitespace":
        df, msg = cleaner.trim_whitespace(data_mgr.current_df)
        data_mgr.current_df = df
        logger.log("Trim Whitespace", msg)

    elif action == "drop_column":
        col = payload.get("column")
        df, msg = cleaner.drop_column(data_mgr.current_df, col)
        data_mgr.current_df = df
        logger.log("Drop Column", msg)

    elif action == "remove_outliers":
        col = payload.get("column")
        df, msg, _ = cleaner.remove_outliers_iqr(data_mgr.current_df, col)
        data_mgr.current_df = df
        logger.log("Remove Outliers", msg)

    elif action == "handle_missing":
        col = payload.get("column", "all")
        strategy = payload.get("strategy", "median")
        custom_val = payload.get("custom_val")
        df, msg = cleaner.handle_missing(data_mgr.current_df, column=col, strategy=strategy, custom_val=custom_val)
        data_mgr.current_df = df
        logger.log("Handle Missing", msg)

    else:
        return jsonify({"success": False, "message": f"Unknown action: {action}"}), 400

    return jsonify({"success": True, "message": msg, "data": build_state_response(data_mgr, logger, sid)})

@app.route("/api/undo", methods=["POST"])
def undo_action():
    sid, data_mgr, logger = get_session_context()
    if not data_mgr.has_data():
        return jsonify({"success": False, "message": "No dataset loaded."}), 400

    success, msg = data_mgr.undo()
    if success:
        logger.log("Undo", "Reverted last cleaning operation.")
        return jsonify({"success": True, "message": msg, "data": build_state_response(data_mgr, logger, sid)})
    return jsonify({"success": False, "message": msg}), 400

@app.route("/api/reset", methods=["POST"])
def reset():
    sid, data_mgr, logger = get_session_context()
    if not data_mgr.has_data():
        return jsonify({"success": False, "message": "No dataset loaded."}), 400

    success, msg = data_mgr.reset_to_raw()
    if success:
        logger.log("Reset", "Dataset restored to original loaded state.")
        return jsonify({"success": True, "message": msg, "data": build_state_response(data_mgr, logger, sid)})
    return jsonify({"success": False, "message": msg}), 400

@app.route("/api/stats", methods=["GET"])
def get_stats():
    sid, data_mgr, _ = get_session_context()
    if not data_mgr.has_data():
        return jsonify({"numeric": {}, "categorical": {}})

    df = data_mgr.current_df
    num_summary = stats_engine.get_numeric_summary(df)
    numeric_data = num_summary.to_dict() if not num_summary.empty else {}

    cat_cols = [c for c in df.columns if not pd.api.types.is_numeric_dtype(df[c])]
    categorical_data = {}
    for col in cat_cols:
        cat_summary = stats_engine.get_categorical_summary(df, col)
        categorical_data[col] = [
            {"category": "<Missing>" if pd.isna(k) else str(k), "count": int(v["count"]), "percentage": float(v["percentage"])}
            for k, v in cat_summary.iterrows()
        ]

    return jsonify({"numeric": numeric_data, "categorical": categorical_data})

@app.route("/api/chart-data", methods=["GET"])
def chart_data():
    sid, data_mgr, _ = get_session_context()
    if not data_mgr.has_data():
        return jsonify({"labels": [], "values": []})

    col = request.args.get("column")
    chart_type = request.args.get("type", "histogram")
    df = data_mgr.current_df

    # Match column flexibly (exact or stripped)
    matching_cols = [c for c in df.columns if c == col or c.strip() == (col or "").strip()]
    if not matching_cols:
        return jsonify({"labels": [], "values": []})

    target_col = matching_cols[0]

    if chart_type == "histogram" and pd.api.types.is_numeric_dtype(df[target_col]):
        clean_series = df[target_col].dropna()
        if clean_series.empty:
            return jsonify({"labels": [], "values": []})
        counts, bin_edges = np.histogram(clean_series, bins=10)
        labels = [f"{bin_edges[i]:.1f}–{bin_edges[i+1]:.1f}" for i in range(len(counts))]
        return jsonify({"labels": labels, "values": [int(x) for x in counts], "is_numeric": True})

    counts = df[target_col].astype(str).value_counts().head(12)
    return jsonify({"labels": counts.index.tolist(), "values": [int(x) for x in counts.values], "is_numeric": False})

@app.route("/api/export/csv")
def export_csv():
    sid, data_mgr, _ = get_session_context()
    if not data_mgr.has_data():
        return "No data to export", 400

    output = io.StringIO()
    data_mgr.current_df.to_csv(output, index=False, encoding="utf-8")
    output.seek(0)
    bytes_data = io.BytesIO(output.getvalue().encode("utf-8"))

    filename = f"cleaned_{data_mgr.source_name or 'dataset.csv'}"
    return send_file(bytes_data, mimetype="text/csv", as_attachment=True, download_name=filename)

@app.route("/api/export/json")
def export_json():
    sid, data_mgr, _ = get_session_context()
    if not data_mgr.has_data():
        return "No data to export", 400

    json_str = data_mgr.current_df.to_json(orient="records", indent=2)
    bytes_data = io.BytesIO(json_str.encode("utf-8"))
    filename = f"cleaned_{os.path.splitext(data_mgr.source_name or 'dataset')[0]}.json"
    return send_file(bytes_data, mimetype="application/json", as_attachment=True, download_name=filename)

@app.route("/api/export/report")
def export_report():
    sid, _, logger = get_session_context()
    report_text = logger.get_report_text()
    bytes_data = io.BytesIO(report_text.encode("utf-8"))
    return send_file(bytes_data, mimetype="text/plain", as_attachment=True, download_name="cleaning_audit_report.txt")

def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000")

if __name__ == "__main__":
    threading.Timer(1.2, open_browser).start()
    app.run(host="127.0.0.1", port=5000, debug=False)
