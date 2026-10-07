# Rebuild this dashboard in Power BI (about 2–3 hours)

Do this yourself so you can show and explain a real Power BI file (.pbix) in an interview.

## 1. Load the data
1. Power BI Desktop → **Get data → Text/CSV** → `data/clean/tools.csv` → **Transform Data**.
2. Repeat for `data/clean/calibration_events.csv`.
3. In Power Query, check the column types: dates as *Date*, `cost_eur` as *Decimal*, `turnaround_days` as *Whole number*. **Close & Apply**.
4. **Model view:** drag `tools[tool_id]` onto `calibration_events[tool_id]` (one-to-many).

## 2. Create the measures (Modeling → New measure)

```DAX
ReportDate = DATE(2026, 10, 7)

Active Tools =
CALCULATE(COUNTROWS(tools), NOT tools[status] IN {"Lost", "Out of Service"})

Overdue Tools =
CALCULATE([Active Tools], tools[next_due_date] < [ReportDate])

Overdue % = DIVIDE([Overdue Tools], [Active Tools])

Due Next 30 Days =
CALCULATE([Active Tools],
    tools[next_due_date] >= [ReportDate],
    tools[next_due_date] <= [ReportDate] + 30)

Calibrations 12M =
CALCULATE(COUNTROWS(calibration_events),
    calibration_events[calibration_date] >= DATE(2025, 10, 1),
    calibration_events[calibration_date] <= DATE(2026, 9, 30))

Pass Rate 12M =
DIVIDE(
    CALCULATE([Calibrations 12M], calibration_events[result] = "Pass"),
    [Calibrations 12M])

Avg Turnaround 12M =
CALCULATE(AVERAGE(calibration_events[turnaround_days]),
    calibration_events[calibration_date] >= DATE(2025, 10, 1),
    calibration_events[calibration_date] <= DATE(2026, 9, 30))

Cost 12M =
CALCULATE(SUM(calibration_events[cost_eur]),
    calibration_events[calibration_date] >= DATE(2025, 10, 1),
    calibration_events[calibration_date] <= DATE(2026, 9, 30))
```

## 3. Build the page
| Visual | Fields |
|---|---|
| 6 **Card** visuals | Active Tools, Overdue Tools, Due Next 30 Days, Pass Rate 12M, Avg Turnaround 12M, Cost 12M |
| **Slicer** (buttons) | tools[department] |
| **Clustered bar chart** | Y: tools[department], X: Overdue % → add a constant line at 5% |
| **Clustered bar chart** | Y: tools[tool_type], X: Cost 12M |
| **Column chart** | X: calibration month, Y: Calibrations 12M |
| **Line chart** | X: calibration month, Y: Pass Rate 12M → constant line at 85% |
| **Table** | tool_id, tool_type, department, location, next_due_date, filtered to overdue + due in 30 days |

Tip: add a month column in Power Query (`Date.StartOfMonth`) for the monthly charts.

## 4. Check your numbers
Your Power BI figures must match the SQL output:
**475 active · 25 overdue (5.3%) · 48 due in 30 days · 651 calibrations · 84.0% pass rate · 5.7 days turnaround · EUR 43,486 cost.**

## 5. Publish
Save as `tool_calibration_kpi.pbix`, take a screenshot for your portfolio, and add the .pbix to the GitHub repository.
