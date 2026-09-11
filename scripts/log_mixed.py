"""Append mixed-session entries. Usage: log_mixed.py <kind> <query> <finding> <track>"""
import sys
from pathlib import Path
from datetime import datetime
kind, query, finding, track = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
ts = datetime.now().strftime("%H:%M:%S")
with open(r"C:\Hiver\research\mixed_18min_log.md", "a", encoding="utf-8") as f:
    f.write(f"\n## {ts} [{kind}] {query}\n- finding: {finding}\n")
with open(r"C:\Hiver\research\research_log.md", "a", encoding="utf-8") as f:
    f.write(f"- DATE: 2026-09-10 / QUERY: {query} / SOURCE: {kind} / KEY FINDING: {finding} / RELEVANCE: {track} / IMPACT: mixed-18min session\n")
print(f"logged {kind} {ts}")
