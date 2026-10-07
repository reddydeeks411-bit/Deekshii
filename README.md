# 📊 Workforce Attrition Patterns & Risk Hotspot Analysis

**Palo Alto Networks — HR Analytics Project**

A comprehensive data science project analyzing employee attrition risk at Palo Alto Networks. Includes exploratory data analysis (EDA), KPI computation, an interactive Streamlit dashboard, and detailed reports with actionable recommendations.

## Project Structure

```text
workforce-attrition-analysis/
├── data/
│   └── attrition.csv                # HR attrition dataset (1,470 employees)
├── notebooks/
│   └── eda.ipynb                    # Exploratory Data Analysis notebook
├── report/
│   ├── research_paper.md            # Full research paper with methodology & findings
│   └── executive_summary.md         # One-page summary for stakeholders
├── src/
│   ├── __init__.py
│   ├── cleaning.py                  # Data loading, cleaning & feature engineering
│   └── kpis.py                      # KPI computation functions
├── app.py                           # Streamlit interactive dashboard
├── requirements.txt                 # Python dependencies
└── README.md                        # This file
```

## Tech Stack

| Tool | Purpose |
|------|---------|
| **Python** | Core language |
| **pandas / numpy** | Data wrangling |
| **matplotlib / seaborn** | Static visualizations (notebook) |
| **plotly** | Interactive charts (dashboard) |
| **Streamlit** | Web dashboard framework |

## Setup Instructions

```bash
# 1. Clone or download the project
# 2. Install dependencies
pip install -r requirements.txt
```

## How to Run

### Interactive Dashboard
```bash
streamlit run app.py
```
The dashboard opens at `http://localhost:8501` with:
- **Sidebar filters**: Department, Job Role, Tenure, OverTime, Travel, Demographics
- **KPI cards**: Attrition Rate, Employees, Exited, Early-Tenure Rate, Workload Index
- **5 tabs**: Attrition Overview, Dept & Role Heatmaps, Demographic Explorer, Tenure & Workload, Auto-generated Insights
- **CSV export** of filtered data

### EDA Notebook
```bash
jupyter notebook notebooks/eda.ipynb
```

## Key Features

- **Modular Code**: Reusable `cleaning.py` and `kpis.py` modules accept filtered DataFrames
- **Interactive Dashboard**: Filter by department, role, tenure, overtime, travel, age, gender, education
- **Risk Hotspot Detection**: Auto-flags segments with above-average attrition rates
- **5 KPIs**: Overall Rate, Dept Rate, Role Rate, Early-Tenure Rate, Workload Attrition Index
- **Auto-Generated Insights**: Top 3 risk segments dynamically computed from current filters
- **Professional Reports**: Research paper with real computed numbers + executive summary

## Key Findings (Summary)

| Risk Factor | Attrition Rate | vs. Overall (26.5%) |
|---|---|---|
| OverTime = Yes | 46.3% | +19.8pp |
| OT + Frequent Travel | 51.7% | +25.2pp |
| Early Tenure (0-2 yrs) | 33.3% | +6.8pp |
| Single employees | 33.1% | +6.6pp |
| HR Department | 36.5% | +10.0pp |

## Screenshots

*(Add screenshots of the Streamlit dashboard here)*

## Author

*(Your name here)*
