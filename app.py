import os
import io
import json
import webbrowser
import threading
from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
import numpy as np

from core.data_manager import DataManager
from core.audit_logger import AuditLogger
from core.exporter import save_csv, save_report
import core.cleaner as cleaner
import core.stats_engine as stats_engine

app = Flask(__name__)
app.config["SECRET_KEY"] = "csv-cleaner-secret-key"

data_mgr = DataManager()
logger = AuditLogger()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/load-sample", methods=["POST"])
def load_sample():
    key = request.json.get("sample", "students")
    success, msg = data_mgr.load_sample(key)
    if success:
        logger.clear()
        name = "Students Dataset (Dirty)" if key == "students" else "Sales Dataset (Dirty)"
        logger.log("Sample Loaded", f"Loaded bundled sample: {name}")
        return jsonify({"success": True, "message": msg, "data": get_state()})
    return jsonify({"success": False, "message": msg}), 400

@app.route("/api/upload", methods=["POST"])
def upload_file():
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
        return jsonify({"success": True, "message": f"Uploaded {file.filename} successfully.", "data": get_state()})
    except Exception as e:
        return jsonify({"success": False, "message": f"Failed to parse CSV: {str(e)}"}), 400

@app.route("/api/state", methods=["GET"])
def get_state_route():
    return jsonify(get_state())

@app.route("/api/clean", methods=["POST"])
def clean_action():
    if not data_mgr.has_data():
        return jsonify({"success": False, "message": "No dataset loaded."}), 400

    payload = request.json or {}
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

    return jsonify({"success": True, "message": msg, "data": get_state()})

@app.route("/api/undo", methods=["POST"])
def undo_action():
    if not data_mgr.has_data():
        return jsonify({"success": False, "message": "No dataset loaded."}), 400

    success, msg = data_mgr.undo()
    if success:
        logger.log("Undo", "Reverted last cleaning operation.")
        return jsonify({"success": True, "message": msg, "data": get_state()})
    return jsonify({"success": False, "message": msg}), 400

@app.route("/api/reset", methods=["POST"])
def reset():
    if not data_mgr.has_data():
        return jsonify({"success": False, "message": "No dataset loaded."}), 400

    success, msg = data_mgr.reset_to_raw()
    if success:
        logger.log("Reset", "Dataset restored to original loaded state.")
        return jsonify({"success": True, "message": msg, "data": get_state()})
    return jsonify({"success": False, "message": msg}), 400

@app.route("/api/stats", methods=["GET"])
def get_stats():
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
    if not data_mgr.has_data():
        return jsonify({"labels": [], "values": []})

    col = request.args.get("column")
    chart_type = request.args.get("type", "histogram")
    df = data_mgr.current_df

    if not col or col not in df.columns:
        return jsonify({"labels": [], "values": []})

    if chart_type == "histogram" and pd.api.types.is_numeric_dtype(df[col]):
        clean_series = df[col].dropna()
        if clean_series.empty:
            return jsonify({"labels": [], "values": []})
        counts, bin_edges = np.histogram(clean_series, bins=10)
        labels = [f"{bin_edges[i]:.1f}-{bin_edges[i+1]:.1f}" for i in range(len(counts))]
        return jsonify({"labels": labels, "values": counts.tolist(), "is_numeric": True})

    counts = df[col].astype(str).value_counts().head(12)
    return jsonify({"labels": counts.index.tolist(), "values": counts.values.tolist(), "is_numeric": False})

@app.route("/api/export/csv")
def export_csv():
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
    if not data_mgr.has_data():
        return "No data to export", 400

    json_str = data_mgr.current_df.to_json(orient="records", indent=2)
    bytes_data = io.BytesIO(json_str.encode("utf-8"))
    filename = f"cleaned_{os.path.splitext(data_mgr.source_name or 'dataset')[0]}.json"
    return send_file(bytes_data, mimetype="application/json", as_attachment=True, download_name=filename)

@app.route("/api/export/report")
def export_report():
    if not data_mgr.has_data():
        return "No data to export", 400

    report_text = logger.get_report_text()
    bytes_data = io.BytesIO(report_text.encode("utf-8"))
    return send_file(bytes_data, mimetype="text/plain", as_attachment=True, download_name="cleaning_audit_report.txt")

def get_state():
    if not data_mgr.has_data():
        return {
            "has_data": False,
            "filename": "",
            "metrics": {},
            "columns": [],
            "rows": [],
            "audit_logs": [],
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
        "has_data": True,
        "filename": data_mgr.source_name,
        "metrics": metrics,
        "columns": list(df.columns),
        "rows": rows,
        "total_rows": len(df),
        "audit_logs": logger.get_logs(),
        "report_text": logger.get_report_text(),
    }

def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000")

if __name__ == "__main__":
    threading.Timer(1.2, open_browser).start()
    app.run(host="127.0.0.1", port=5000, debug=False)
