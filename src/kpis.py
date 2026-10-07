"""
kpis.py — KPI computation functions for the HR Attrition dashboard.

All functions accept a (filtered) DataFrame so the Streamlit dashboard
can recompute KPIs dynamically based on user-selected filters.

KPIs:
    1. Overall Attrition Rate (%)
    2. Department Attrition Rate
    3. Role Attrition Rate
    4. Early-Tenure Attrition Rate (leavers within first 2 years)
    5. Workload Attrition Index (WAI)

The Workload Attrition Index formula:
    WAI = (attrition rate of employees with OverTime=Yes AND BusinessTravel=Travel-Frequently)
          ÷ (overall attrition rate)
    Interpretation: WAI > 1 ⇒ high-workload employees leave at a higher rate than average.
"""

import pandas as pd
import numpy as np


def overall_attrition_rate(df: pd.DataFrame) -> float:
    """
    Overall Attrition Rate (%).

    Returns the percentage of employees who left (AttritionFlag == 1).
    Returns 0.0 if the DataFrame is empty.
    """
    if df.empty or "AttritionFlag" not in df.columns:
        return 0.0
    return df["AttritionFlag"].mean() * 100


def department_attrition_rate(df: pd.DataFrame) -> pd.DataFrame:
    """
    Attrition rate per Department.

    Returns a DataFrame with columns: Department, Employees, Exited, AttritionRate(%).
    Sorted by AttritionRate descending.
    """
    if df.empty:
        return pd.DataFrame(columns=["Department", "Employees", "Exited", "AttritionRate(%)"])

    grouped = df.groupby("Department").agg(
        Employees=("AttritionFlag", "count"),
        Exited=("AttritionFlag", "sum"),
    ).reset_index()
    grouped["AttritionRate(%)"] = (grouped["Exited"] / grouped["Employees"] * 100).round(1)
    return grouped.sort_values("AttritionRate(%)", ascending=False).reset_index(drop=True)


def role_attrition_rate(df: pd.DataFrame) -> pd.DataFrame:
    """
    Attrition rate per Job Role.

    Returns a DataFrame with columns: JobRole, Employees, Exited, AttritionRate(%).
    Sorted by AttritionRate descending.
    """
    if df.empty:
        return pd.DataFrame(columns=["JobRole", "Employees", "Exited", "AttritionRate(%)"])

    grouped = df.groupby("JobRole").agg(
        Employees=("AttritionFlag", "count"),
        Exited=("AttritionFlag", "sum"),
    ).reset_index()
    grouped["AttritionRate(%)"] = (grouped["Exited"] / grouped["Employees"] * 100).round(1)
    return grouped.sort_values("AttritionRate(%)", ascending=False).reset_index(drop=True)


def early_tenure_attrition_rate(df: pd.DataFrame) -> float:
    """
    Early-Tenure Attrition Rate (%).

    Measures the attrition rate among employees with YearsAtCompany ≤ 2.
    Formula: (leavers with ≤2 yrs) / (all employees with ≤2 yrs) × 100
    Returns 0.0 if no employees fall in this tenure band.
    """
    if df.empty:
        return 0.0
    early = df[df["YearsAtCompany"] <= 2]
    if early.empty:
        return 0.0
    return early["AttritionFlag"].mean() * 100


def workload_attrition_index(df: pd.DataFrame) -> float:
    """
    Workload Attrition Index (WAI).

    Formula:
        WAI = attrition_rate(OverTime=Yes AND BusinessTravel=Travel-Frequently)
              ÷ overall_attrition_rate

    Interpretation:
        WAI = 1.0  → high-workload employees leave at the same rate as average.
        WAI > 1.0  → high-workload employees are at elevated risk.
        WAI < 1.0  → high-workload employees are actually less likely to leave.

    Returns 0.0 if overall attrition is 0 or no employees match the high-workload filter.
    """
    if df.empty:
        return 0.0

    overall_rate = df["AttritionFlag"].mean()
    if overall_rate == 0:
        return 0.0

    # Normalize BusinessTravel and OverTime for comparison (handle title-cased or raw)
    bt_col = df["BusinessTravel"].astype(str).str.lower().str.replace("_", "-")
    ot_col = df["OverTime"].astype(str).str.lower()

    high_workload = df[
        (ot_col == "yes") &
        (bt_col == "travel-frequently")
    ]

    if high_workload.empty:
        return 0.0

    hw_rate = high_workload["AttritionFlag"].mean()
    return round(hw_rate / overall_rate, 2)


def compute_all_kpis(df: pd.DataFrame) -> dict:
    """
    Convenience function that computes all KPIs and returns them in a dict.

    Keys:
        overall_rate        : float (%)
        total_employees     : int
        total_exited        : int
        dept_rates          : pd.DataFrame
        role_rates          : pd.DataFrame
        early_tenure_rate   : float (%)
        workload_index      : float
    """
    return {
        "overall_rate": round(overall_attrition_rate(df), 1),
        "total_employees": len(df),
        "total_exited": int(df["AttritionFlag"].sum()) if not df.empty else 0,
        "dept_rates": department_attrition_rate(df),
        "role_rates": role_attrition_rate(df),
        "early_tenure_rate": round(early_tenure_attrition_rate(df), 1),
        "workload_index": workload_attrition_index(df),
    }


# ---------------------------------------------------------------------------
# Quick test when run directly
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import sys
    sys.path.insert(0, ".")
    from src.cleaning import prepare_data

    df = prepare_data()
    kpis = compute_all_kpis(df)

    print("\n" + "=" * 60)
    print("KPI RESULTS")
    print("=" * 60)
    print(f"  Overall Attrition Rate : {kpis['overall_rate']}%")
    print(f"  Total Employees        : {kpis['total_employees']}")
    print(f"  Total Exited           : {kpis['total_exited']}")
    print(f"  Early-Tenure Attrition : {kpis['early_tenure_rate']}%")
    print(f"  Workload Attrition Idx : {kpis['workload_index']}x")
    print(f"\n--- Department Attrition ---")
    print(kpis["dept_rates"].to_string(index=False))
    print(f"\n--- Role Attrition ---")
    print(kpis["role_rates"].to_string(index=False))
