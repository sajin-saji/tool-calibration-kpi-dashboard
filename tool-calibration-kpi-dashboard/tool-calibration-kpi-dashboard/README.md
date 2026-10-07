# Tool Calibration KPI Dashboard

An end-to-end data project for a tool center: raw tool and calibration records are cleaned with Python, stored in a SQLite database, analyzed with SQL and turned into an interactive KPI dashboard that shows which tools need calibration and where the backlog is.

**Live dashboard:** [sajin-saji.github.io/tool-calibration-kpi-dashboard/dashboard/](https://sajin-saji.github.io/tool-calibration-kpi-dashboard/dashboard/)
**Project report (PDF):** [docs/Project_Report.pdf](docs/Project_Report.pdf)

> All data is randomly generated (`src/generate_data.py`) and does not describe any real company. Errors were added on purpose so that the cleaning step has real work to do.

![Dashboard](docs/dashboard.png)

## Results (reporting date 07 Oct 2026)

| KPI | Value |
|---|---|
| Active tools | 475 |
| Overdue | 25 (5.3%, limit 5%) |
| Due in next 30 days | 48 |
| First-time pass rate (Oct 2025 – Sep 2026) | 84.0% (target 85%) |
| Average turnaround | 5.7 days |
| Calibration cost (651 jobs) | EUR 43,486 |

**Key findings**
- The overdue backlog is concentrated in **Cabin Installation (6.8%), Logistics (6.7%) and Fuselage Assembly (6.5%)**.
- **48 tools fall due within 30 days**; scheduling them now keeps the overdue rate from rising.
- The first-time pass rate **dropped to 69–72% in Aug–Sep 2026**.
- **Pressure gauges** are the largest cost driver (EUR 12,457); **multimeters** have the highest fail rate (11.3%).

## Pipeline

```
src/generate_data.py   ->  data/raw/*.csv             500 tools, 1,340 events, deliberate errors
src/clean_data.py      ->  data/clean/*.csv           cleaned data
                       ->  data/calibration.db        SQLite database
                       ->  data/cleaning_report.txt   log of every fix
sql/kpi_queries.sql                                   6 KPI queries
src/build_dashboard.py ->  dashboard/index.html       interactive dashboard
```

### Data cleaning
| Problem in raw data | Fix | Rows |
|---|---|---|
| Duplicate tool rows / calibration events | Removed | 8 / 15 |
| Department typos (`QA Lab`, `Fuselage assy`) | Mapped to standard names | 15 |
| Mixed date formats (`DD.MM.YYYY`) | Converted to ISO | 20 |
| Missing next-due dates | Recomputed from last calibration + interval | 12 |
| Zero or negative costs | Removed as invalid | 10 |

## Run it

```bash
pip install pandas
python src/generate_data.py
python src/clean_data.py
sqlite3 data/calibration.db < sql/kpi_queries.sql
python src/build_dashboard.py
```

## Repository
| Path | Content |
|---|---|
| `data/` | raw and clean CSVs, SQLite database, cleaning report |
| `sql/` | KPI queries |
| `src/` | Python scripts |
| `dashboard/` | interactive dashboard (`index.html`) |
| `docs/` | project report (PDF), screenshot, Power BI rebuild guide |

## Tools
Python (pandas) · SQLite / SQL · HTML, SVG, JavaScript · Power BI (rebuild guide in `docs/power_bi_guide.md`)

## Author
**Sajin Saji**, M.Eng Mechatronics & Cyber-Physical Systems, TH Deggendorf
[sajin-saji.github.io](https://sajin-saji.github.io) · [LinkedIn](https://linkedin.com/in/sajin-saji-4762561b5) · [GitHub](https://github.com/sajin-saji)
