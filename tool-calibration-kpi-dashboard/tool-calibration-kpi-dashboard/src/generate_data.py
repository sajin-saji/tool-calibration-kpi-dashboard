"""Generate a SYNTHETIC tool-management dataset for a portfolio project.

All data is randomly generated. It does not describe any real company.
Deliberate data-quality problems are injected so that clean_data.py has real work to do.
"""
import csv, random
from datetime import date, timedelta
from pathlib import Path

random.seed(42)
AS_OF = date(2026, 10, 7)
OUT = Path(__file__).resolve().parent.parent / "data" / "raw"
OUT.mkdir(parents=True, exist_ok=True)

TOOL_TYPES = {  # type: (calibration interval months, cost range EUR, fail prob)
    "Torque Wrench": (6, (45, 90), 0.08),
    "Digital Caliper": (12, (25, 45), 0.03),
    "Micrometer": (12, (30, 55), 0.04),
    "Pressure Gauge": (6, (60, 120), 0.07),
    "Multimeter": (12, (50, 95), 0.04),
    "Crimping Tool": (6, (35, 70), 0.10),
    "Dial Indicator": (12, (30, 50), 0.05),
    "Height Gauge": (12, (70, 140), 0.03),
}
DEPARTMENTS = {
    "Fuselage Assembly": 0.30,
    "Wing Assembly": 0.20,
    "Cabin Installation": 0.20,
    "Quality Lab": 0.15,
    "Logistics": 0.15,
}
DEPT_LATE_FACTOR = {"Fuselage Assembly": 1.0, "Wing Assembly": 0.8, "Cabin Installation": 1.6,
                    "Quality Lab": 0.4, "Logistics": 1.3}
LOCATIONS = ["Hall 1", "Hall 2", "Hall 3", "Hall 4", "Tool Crib A", "Tool Crib B"]

def add_months(d, m):
    y, mo = divmod(d.month - 1 + m, 12)
    day = min(d.day, 28)
    return date(d.year + y, mo + 1, day)

tools, events = [], []
eid = 1
for i in range(1, 501):
    ttype = random.choice(list(TOOL_TYPES))
    interval, (cmin, cmax), pfail = TOOL_TYPES[ttype]
    dept = random.choices(list(DEPARTMENTS), weights=DEPARTMENTS.values())[0]
    purchase = AS_OF - timedelta(days=random.randint(400, 3000))
    # calibration history over the last ~24 months
    d = max(purchase, AS_OF - timedelta(days=760)) + timedelta(days=random.randint(0, interval * 30))
    last_cal, last_result = None, None
    while d <= AS_OF:
        r = random.random()
        result = "Fail" if r < pfail else ("Adjusted" if r < pfail + 0.12 else "Pass")
        cost = round(random.uniform(cmin, cmax) * (1.6 if result == "Fail" else 1.0), 2)
        turnaround = max(1, int(random.gauss(6, 2.5)) + (5 if result == "Fail" else 0))
        events.append([f"EV{eid:05d}", f"T{i:04d}", d.isoformat(), result, cost, turnaround])
        eid += 1
        last_cal, last_result = d, result
        # next calibration: on time or late, depending on department discipline
        late = int(abs(random.gauss(0, 18)) * DEPT_LATE_FACTOR[dept]) if random.random() < 0.35 else 0
        d = add_months(d, interval) + timedelta(days=late)
    # some tools miss their latest calibration (realistic backlog, worse in some departments)
    if random.random() < 0.055 * DEPT_LATE_FACTOR[dept] and len(events) > 1 and events[-1][1] == f"T{i:04d}" \
            and events[-2][1] == f"T{i:04d}":
        events.pop(); eid -= 1
        last_cal = date.fromisoformat(events[-1][2]); last_result = events[-1][3]
    next_due = add_months(last_cal, interval) if last_cal else None
    s = random.random()
    status = ("In Calibration" if s < 0.05 else "Out of Service" if s < 0.08 else
              "Lost" if s < 0.095 else "In Use")
    checkouts = max(0, int(random.gauss(14, 7)))
    tools.append([f"T{i:04d}", ttype, dept, random.choice(LOCATIONS), purchase.isoformat(),
                  last_cal.isoformat() if last_cal else "", interval,
                  next_due.isoformat() if next_due else "", status, checkouts])

# ---- inject data-quality problems ----
for row in random.sample(tools, 25):          # inconsistent casing / whitespace
    row[1] = random.choice([row[1].lower(), row[1].upper(), f"  {row[1]} "])
for row in random.sample(tools, 15):          # department typos
    row[2] = {"Fuselage Assembly": "Fuselage assy", "Wing Assembly": "wing assembly",
              "Cabin Installation": "Cabin Instal.", "Quality Lab": "QA Lab",
              "Logistics": "logistics "}[row[2]]
for row in random.sample(tools, 20):          # mixed date format DD.MM.YYYY
    if row[5]:
        y, m, dd = row[5].split("-"); row[5] = f"{dd}.{m}.{y}"
for row in random.sample(tools, 12):          # missing next due date (must be recomputed)
    row[7] = ""
tools += [list(r) for r in random.sample(tools, 8)]   # duplicate rows
random.shuffle(tools)
for ev in random.sample(events, 10):          # negative / zero costs
    ev[4] = -ev[4] if random.random() < 0.5 else 0
events += [list(e) for e in random.sample(events, 15)]  # duplicate events

with open(OUT / "tools_raw.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["tool_id", "tool_type", "department", "location", "purchase_date",
                "last_calibration_date", "calibration_interval_months", "next_due_date",
                "status", "checkouts_last_90d"])
    w.writerows(tools)
with open(OUT / "calibration_events_raw.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["event_id", "tool_id", "calibration_date", "result", "cost_eur", "turnaround_days"])
    w.writerows(events)
print(f"tools rows: {len(tools)}  events rows: {len(events)}")
