"""Inject the cleaned SQLite data into the dashboard template -> dashboard/index.html"""
import json, sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
con = sqlite3.connect(ROOT / "data" / "calibration.db")
tools = con.execute("SELECT tool_id, tool_type, department, location, next_due_date, status "
                    "FROM tools ORDER BY tool_id").fetchall()
events = con.execute("SELECT tool_id, calibration_date, result, cost_eur, turnaround_days "
                     "FROM calibration_events ORDER BY calibration_date").fetchall()
data = {"tools": tools, "events": events}
tpl = (ROOT / "dashboard" / "template.html").read_text()
out = tpl.replace("/*__DATA__*/null", json.dumps(data, separators=(",", ":")))
# artifact version (the host adds the page skeleton) and a standalone version for GitHub Pages
(ROOT / "dashboard" / "dashboard_artifact.html").write_text(out)
page = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        '<style>body{margin:0}</style>\n</head>\n<body>\n' + out + '\n</body>\n</html>\n')
(ROOT / "dashboard" / "index.html").write_text(page)
print(f"dashboard/index.html written ({len(out)//1024} KB, {len(tools)} tools, {len(events)} events)")
