from datetime import datetime
from typing import List, Dict, Any

class AuditLogger:
    def __init__(self):
        self.entries: List[Dict[str, Any]] = []

    def log(self, action: str, details: str) -> None:
        entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "action": action,
            "details": details,
        }
        self.entries.append(entry)

    def get_logs(self) -> List[Dict[str, Any]]:
        return list(self.entries)

    def get_report_text(self) -> str:
        if not self.entries:
            return "No cleaning actions performed yet."

        lines = [
            "=" * 70,
            "       CSV DATA CLEANER & ANALYTICS STUDIO — AUDIT REPORT",
            "=" * 70,
            f"Generated At: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Total Transformations: {len(self.entries)}",
            "-" * 70,
            "",
        ]

        for i, entry in enumerate(self.entries, start=1):
            lines.append(f"[{i}] {entry['timestamp']} — {entry['action']}")
            lines.append(f"    Details: {entry['details']}")
            lines.append("")

        lines.append("=" * 70)
        lines.append("End of Audit Report.")
        lines.append("=" * 70)
        return "\n".join(lines)

    def clear(self) -> None:
        self.entries.clear()
