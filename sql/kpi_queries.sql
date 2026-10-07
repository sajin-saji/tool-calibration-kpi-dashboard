-- Tool Calibration KPI queries (SQLite)
-- Reporting date: 2026-10-07. Run with:  sqlite3 data/calibration.db < sql/kpi_queries.sql
.headers on
.mode column

-- 1. Headline KPIs for active tools (not Lost / Out of Service)
SELECT
  COUNT(*)                                                             AS active_tools,
  SUM(next_due_date < '2026-10-07')                                    AS overdue,
  ROUND(100.0 * SUM(next_due_date < '2026-10-07') / COUNT(*), 1)       AS overdue_pct,
  SUM(next_due_date BETWEEN '2026-10-07' AND date('2026-10-07', '+30 days')) AS due_next_30_days
FROM tools
WHERE status NOT IN ('Lost', 'Out of Service');

-- 2. First-time pass rate and average turnaround, last 12 complete months (Oct 2025 - Sep 2026)
SELECT
  COUNT(*)                                                   AS calibrations,
  ROUND(100.0 * SUM(result = 'Pass') / COUNT(*), 1)          AS pass_rate_pct,
  ROUND(100.0 * SUM(result = 'Fail') / COUNT(*), 1)          AS fail_rate_pct,
  ROUND(AVG(turnaround_days), 1)                             AS avg_turnaround_days,
  ROUND(SUM(cost_eur), 0)                                    AS total_cost_eur
FROM calibration_events
WHERE calibration_date BETWEEN '2025-10-01' AND '2026-09-30';

-- 3. Overdue rate by department (where to act first)
SELECT
  department,
  COUNT(*)                                                       AS active_tools,
  SUM(next_due_date < '2026-10-07')                              AS overdue,
  ROUND(100.0 * SUM(next_due_date < '2026-10-07') / COUNT(*), 1) AS overdue_pct
FROM tools
WHERE status NOT IN ('Lost', 'Out of Service')
GROUP BY department
ORDER BY overdue_pct DESC;

-- 4. Calibration cost and fail rate by tool type, last 12 complete months (Oct 2025 - Sep 2026)
SELECT
  t.tool_type,
  COUNT(*)                                               AS calibrations,
  ROUND(SUM(e.cost_eur), 0)                              AS cost_eur,
  ROUND(100.0 * SUM(e.result = 'Fail') / COUNT(*), 1)    AS fail_rate_pct
FROM calibration_events e
JOIN tools t ON t.tool_id = e.tool_id
WHERE e.calibration_date BETWEEN '2025-10-01' AND '2026-09-30'
GROUP BY t.tool_type
ORDER BY cost_eur DESC;

-- 5. Monthly trend: calibrations and pass rate
SELECT
  substr(calibration_date, 1, 7)                      AS month,
  COUNT(*)                                            AS calibrations,
  ROUND(100.0 * SUM(result = 'Pass') / COUNT(*), 1)   AS pass_rate_pct
FROM calibration_events
WHERE calibration_date BETWEEN '2025-10-01' AND '2026-09-30'
GROUP BY month
ORDER BY month;

-- 6. Action list: active tools due in the next 30 days
SELECT tool_id, tool_type, department, location, next_due_date
FROM tools
WHERE status NOT IN ('Lost', 'Out of Service')
  AND next_due_date BETWEEN '2026-10-07' AND date('2026-10-07', '+30 days')
ORDER BY next_due_date;
