"""Audit Logger module.

Tracks timestamped history of all data cleaning transformations applied
during the session and generates an exportable audit changelog.
"""

from datetime import datetime
from typing import List, Dict, Any


class AuditLogger:
    """In-memory audit logger for data cleaning transformations."""

    def __init__(self) -> None:
        self.entries: List[Dict[str, Any]] = []

    def log(self, action: str, details: str) -> None:
        """Records a new cleaning action with current timestamp."""
        entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "action": action,
            "details": details,
        }
        self.entries.append(entry)

    def get_logs(self) -> List[Dict[str, Any]]:
        """Returns the list of all recorded log entries."""
        return list(self.entries)

    def get_report_text(self) -> str:
        """Formats the audit log as a clean text document."""
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
        """Clears all audit records."""
        self.entries.clear()
