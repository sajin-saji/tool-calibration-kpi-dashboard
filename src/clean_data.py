"""Clean the raw tool and calibration data and load it into a SQLite database.

Steps (each logged in data/cleaning_report.txt):
 1. Remove duplicate rows
 2. Standardize tool types and department names (casing, whitespace, typos)
 3. Parse mixed date formats (YYYY-MM-DD and DD.MM.YYYY)
 4. Recompute missing next-due dates from last calibration + interval
 5. Remove calibration events with invalid (zero/negative) cost
 6. Write clean CSVs and data/calibration.db
"""
import sqlite3
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW, CLEAN = ROOT / "data" / "raw", ROOT / "data" / "clean"
CLEAN.mkdir(parents=True, exist_ok=True)
log = []

tools = pd.read_csv(RAW / "tools_raw.csv", dtype=str)
events = pd.read_csv(RAW / "calibration_events_raw.csv", dtype=str)
log.append(f"Loaded {len(tools)} tool rows and {len(events)} calibration event rows.")

# 1. duplicates
n = len(tools); tools = tools.drop_duplicates(); log.append(f"Removed {n - len(tools)} duplicate tool rows.")
n = len(events); events = events.drop_duplicates(); log.append(f"Removed {n - len(events)} duplicate event rows.")

# 2. standardize text
tools["tool_type"] = tools["tool_type"].str.strip().str.title()
DEPT_MAP = {"fuselage assy": "Fuselage Assembly", "wing assembly": "Wing Assembly",
            "cabin instal.": "Cabin Installation", "qa lab": "Quality Lab", "logistics": "Logistics"}
before = tools["department"].copy()
tools["department"] = tools["department"].str.strip()
tools["department"] = tools["department"].apply(lambda d: DEPT_MAP.get(d.lower(), d))
log.append(f"Standardized {int((before != tools['department']).sum())} department names "
           f"and normalized tool-type casing/whitespace.")

# 3. dates
def parse_date(s):
    if pd.isna(s) or s == "":
        return pd.NaT
    return pd.to_datetime(s, format="%d.%m.%Y") if "." in s else pd.to_datetime(s, format="%Y-%m-%d")

mixed = tools["last_calibration_date"].fillna("").str.contains(r"\.").sum()
for col in ["purchase_date", "last_calibration_date", "next_due_date"]:
    tools[col] = tools[col].apply(parse_date)
events["calibration_date"] = pd.to_datetime(events["calibration_date"])
log.append(f"Converted {mixed} dates from DD.MM.YYYY to ISO format.")

# 4. recompute missing next due date
tools["calibration_interval_months"] = tools["calibration_interval_months"].astype(int)
missing = tools["next_due_date"].isna()
tools.loc[missing, "next_due_date"] = tools.loc[missing].apply(
    lambda r: r["last_calibration_date"] + pd.DateOffset(months=r["calibration_interval_months"]), axis=1)
log.append(f"Recomputed {int(missing.sum())} missing next-due dates.")

# 5. invalid costs
events["cost_eur"] = events["cost_eur"].astype(float)
events["turnaround_days"] = events["turnaround_days"].astype(int)
bad = events["cost_eur"] <= 0
events = events[~bad]
log.append(f"Removed {int(bad.sum())} events with zero or negative cost.")

tools["checkouts_last_90d"] = tools["checkouts_last_90d"].astype(int)
for col in ["purchase_date", "last_calibration_date", "next_due_date"]:
    tools[col] = tools[col].dt.strftime("%Y-%m-%d")
events["calibration_date"] = events["calibration_date"].dt.strftime("%Y-%m-%d")

# 6. save
tools.sort_values("tool_id").to_csv(CLEAN / "tools.csv", index=False)
events.sort_values("event_id").to_csv(CLEAN / "calibration_events.csv", index=False)
db = ROOT / "data" / "calibration.db"
db.unlink(missing_ok=True)
with sqlite3.connect(db) as con:
    tools.to_sql("tools", con, index=False)
    events.to_sql("calibration_events", con, index=False)
log.append(f"Saved {len(tools)} clean tools and {len(events)} clean events to CSV and SQLite.")

(ROOT / "data" / "cleaning_report.txt").write_text("\n".join(log) + "\n")
print("\n".join(log))
