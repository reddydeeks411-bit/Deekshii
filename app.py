"""
app.py — Streamlit Dashboard for Workforce Attrition Analysis at Palo Alto Networks.

Run with:  streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.cleaning import prepare_data
from src.kpis import (
    overall_attrition_rate,
    department_attrition_rate,
    role_attrition_rate,
    early_tenure_attrition_rate,
    workload_attrition_index,
    compute_all_kpis,
)

# ──────────────────────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Workforce Attrition Dashboard — Palo Alto Networks",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────────
# CUSTOM CSS
# ──────────────────────────────────────────────────────────────

st.markdown("""
<style>
    /* KPI cards */
    .kpi-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        color: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin-bottom: 10px;
    }
    .kpi-card h3 {
        margin: 0;
        font-size: 14px;
        font-weight: 500;
        opacity: 0.9;
    }
    .kpi-card h1 {
        margin: 5px 0 0 0;
        font-size: 32px;
        font-weight: 700;
    }
    .kpi-danger {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    }
    .kpi-warning {
        background: linear-gradient(135deg, #f6d365 0%, #fda085 100%);
        color: #333;
    }
    .kpi-success {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    }
    .kpi-info {
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        color: #333;
    }
    /* Title */
    .main-title {
        text-align: center;
        font-size: 28px;
        font-weight: 700;
        color: #1a1a2e;
        margin-bottom: 5px;
    }
    .sub-title {
        text-align: center;
        font-size: 14px;
        color: #666;
        margin-bottom: 20px;
    }
    /* High-risk badge */
    .high-risk {
        background-color: #ff4b4b;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────
# DATA LOADING (cached)
# ──────────────────────────────────────────────────────────────

@st.cache_data
def load_and_prepare():
    """Load and prepare data with caching."""
    return prepare_data("data/attrition.csv")


df_full = load_and_prepare()

# ──────────────────────────────────────────────────────────────
# SIDEBAR FILTERS
# ──────────────────────────────────────────────────────────────

st.sidebar.image("https://img.icons8.com/color/96/analytics.png", width=60)
st.sidebar.title("🔍 Filters")
st.sidebar.markdown("---")

# Department filter
all_departments = sorted(df_full["Department"].unique())
selected_departments = st.sidebar.multiselect(
    "Department", all_departments, default=all_departments
)

# Job Role filter (dependent on department)
available_roles = sorted(
    df_full[df_full["Department"].isin(selected_departments)]["JobRole"].unique()
)
selected_roles = st.sidebar.multiselect(
    "Job Role", available_roles, default=available_roles
)

st.sidebar.markdown("---")

# Tenure slider
min_tenure = int(df_full["YearsAtCompany"].min())
max_tenure = int(df_full["YearsAtCompany"].max())
tenure_range = st.sidebar.slider(
    "Years at Company", min_tenure, max_tenure, (min_tenure, max_tenure)
)

# OverTime toggle
overtime_option = st.sidebar.radio("OverTime", ["All", "Yes", "No"], horizontal=True)

# Business Travel selector
travel_options = ["All"] + sorted(df_full["BusinessTravel"].unique().tolist())
travel_selected = st.sidebar.selectbox("Business Travel", travel_options)

st.sidebar.markdown("---")
st.sidebar.subheader("Demographics")

# Age filter
all_age_groups = sorted(df_full["AgeGroup"].unique().tolist())
selected_age_groups = st.sidebar.multiselect(
    "Age Group", all_age_groups, default=all_age_groups
)

# Gender filter
all_genders = sorted(df_full["Gender"].unique())
selected_genders = st.sidebar.multiselect(
    "Gender", all_genders, default=all_genders
)

# Education filter
all_edu = sorted(df_full["EducationLabel"].unique().tolist())
selected_edu = st.sidebar.multiselect(
    "Education Level", all_edu, default=all_edu
)

# ──────────────────────────────────────────────────────────────
# APPLY FILTERS
# ──────────────────────────────────────────────────────────────

df = df_full.copy()
df = df[df["Department"].isin(selected_departments)]
df = df[df["JobRole"].isin(selected_roles)]
df = df[
    (df["YearsAtCompany"] >= tenure_range[0]) &
    (df["YearsAtCompany"] <= tenure_range[1])
]
if overtime_option != "All":
    df = df[df["OverTime"] == overtime_option]
if travel_selected != "All":
    df = df[df["BusinessTravel"] == travel_selected]
df = df[df["AgeGroup"].isin(selected_age_groups)]
df = df[df["Gender"].isin(selected_genders)]
df = df[df["EducationLabel"].isin(selected_edu)]

# ──────────────────────────────────────────────────────────────
# HEADER
# ──────────────────────────────────────────────────────────────

st.markdown('<p class="main-title">📊 Workforce Attrition Patterns & Risk Hotspot Analysis</p>',
            unsafe_allow_html=True)
st.markdown('<p class="sub-title">Palo Alto Networks — HR Analytics Dashboard</p>',
            unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────
# HANDLE EMPTY FILTER RESULTS
# ──────────────────────────────────────────────────────────────

if df.empty:
    st.warning("⚠️ No employees match the current filter selection. Please adjust your filters.")
    st.stop()

# ──────────────────────────────────────────────────────────────
# KPI CARDS
# ──────────────────────────────────────────────────────────────

kpis = compute_all_kpis(df)

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(f"""
    <div class="kpi-card kpi-danger">
        <h3>Attrition Rate</h3>
        <h1>{kpis['overall_rate']}%</h1>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="kpi-card">
        <h3>Total Employees</h3>
        <h1>{kpis['total_employees']:,}</h1>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="kpi-card kpi-warning">
        <h3>Exited</h3>
        <h1>{kpis['total_exited']:,}</h1>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="kpi-card kpi-success">
        <h3>Early-Tenure Attrition</h3>
        <h1>{kpis['early_tenure_rate']}%</h1>
    </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown(f"""
    <div class="kpi-card kpi-info">
        <h3>Workload Attrition Idx</h3>
        <h1>{kpis['workload_index']}x</h1>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ──────────────────────────────────────────────────────────────
# HELPER: attrition rate by group
# ──────────────────────────────────────────────────────────────

def attrition_by_group(data, group_col, sort_by_rate=True):
    """Compute attrition rate and counts by a grouping column."""
    grouped = data.groupby(group_col).agg(
        Employees=("AttritionFlag", "count"),
        Exited=("AttritionFlag", "sum"),
    ).reset_index()
    grouped["AttritionRate(%)"] = (grouped["Exited"] / grouped["Employees"] * 100).round(1)
    grouped["LowSample"] = grouped["Employees"] < 30
    if sort_by_rate:
        grouped = grouped.sort_values("AttritionRate(%)", ascending=False)
    return grouped.reset_index(drop=True)


def flag_text(row, overall_rate):
    """Return '🔴 High-Risk' if rate exceeds overall average."""
    if row["AttritionRate(%)"] > overall_rate:
        return "🔴 High-Risk"
    return ""


# ──────────────────────────────────────────────────────────────
# TABS
# ──────────────────────────────────────────────────────────────

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Attrition Overview",
    "🏢 Department & Role Heatmaps",
    "👥 Demographic Explorer",
    "⏱️ Tenure & Workload",
    "💡 Insights",
])

# ──────────────────────────────────────────────────────────────
# TAB 1: Attrition Overview
# ──────────────────────────────────────────────────────────────
with tab1:
    st.subheader("Overall Attrition Distribution")

    c1, c2 = st.columns(2)
    with c1:
        # Donut chart
        attrition_counts = df["Attrition"].value_counts().reset_index()
        attrition_counts.columns = ["Status", "Count"]
        fig_donut = px.pie(
            attrition_counts, values="Count", names="Status",
            hole=0.55,
            color_discrete_sequence=["#4facfe", "#f5576c"],
            title="Retained vs Exited Employees"
        )
        fig_donut.update_traces(textinfo="percent+value")
        fig_donut.update_layout(height=400)
        st.plotly_chart(fig_donut, use_container_width=True)

    with c2:
        # Attrition rate bar chart by department
        dept_rates = attrition_by_group(df, "Department")
        fig_dept = px.bar(
            dept_rates, x="Department", y="AttritionRate(%)",
            text="AttritionRate(%)",
            color="AttritionRate(%)",
            color_continuous_scale="RdYlGn_r",
            title="Attrition Rate by Department",
            hover_data=["Employees", "Exited"],
        )
        fig_dept.update_traces(texttemplate="%{text}%", textposition="outside")
        fig_dept.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_dept, use_container_width=True)

    # Summary table
    st.subheader("Department Summary")
    dept_summary = dept_rates.copy()
    overall_r = kpis["overall_rate"]
    dept_summary["Risk Flag"] = dept_summary.apply(lambda r: flag_text(r, overall_r), axis=1)
    dept_summary["⚠ Low Sample"] = dept_summary["LowSample"].map({True: "⚠ n<30", False: ""})
    st.dataframe(
        dept_summary[["Department", "Employees", "Exited", "AttritionRate(%)", "Risk Flag", "⚠ Low Sample"]],
        use_container_width=True, hide_index=True
    )

# ──────────────────────────────────────────────────────────────
# TAB 2: Department & Role Heatmaps
# ──────────────────────────────────────────────────────────────
with tab2:
    st.subheader("Attrition Intensity: Department × Job Role")

    # Heatmap
    pivot = df.pivot_table(
        values="AttritionFlag", index="Department", columns="JobRole", aggfunc="mean"
    ) * 100

    fig_hm = px.imshow(
        pivot.round(1),
        text_auto=".1f",
        color_continuous_scale="YlOrRd",
        aspect="auto",
        title="Attrition Rate (%) — Department × Job Role",
        labels=dict(x="Job Role", y="Department", color="Rate (%)"),
    )
    fig_hm.update_layout(height=400)
    st.plotly_chart(fig_hm, use_container_width=True)

    # Ranked bar chart of roles
    st.subheader("Job Roles Ranked by Attrition Rate")
    role_rates = attrition_by_group(df, "JobRole")
    role_rates["Risk Flag"] = role_rates.apply(lambda r: flag_text(r, overall_r), axis=1)

    fig_roles = px.bar(
        role_rates, x="AttritionRate(%)", y="JobRole",
        orientation="h",
        text="AttritionRate(%)",
        color="AttritionRate(%)",
        color_continuous_scale="RdYlGn_r",
        hover_data=["Employees", "Exited"],
        title="Attrition Rate by Job Role (High-Risk = above overall average)"
    )
    fig_roles.update_traces(texttemplate="%{text}%", textposition="outside")
    fig_roles.update_layout(height=450, showlegend=False, yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig_roles, use_container_width=True)

    # Table
    role_display = role_rates.copy()
    role_display["⚠ Low Sample"] = role_display["LowSample"].map({True: "⚠ n<30", False: ""})
    st.dataframe(
        role_display[["JobRole", "Employees", "Exited", "AttritionRate(%)", "Risk Flag", "⚠ Low Sample"]],
        use_container_width=True, hide_index=True
    )

# ──────────────────────────────────────────────────────────────
# TAB 3: Demographic Explorer
# ──────────────────────────────────────────────────────────────
with tab3:
    st.subheader("Attrition by Demographics")

    c1, c2 = st.columns(2)

    with c1:
        # Age Group
        age_data = attrition_by_group(df, "AgeGroup", sort_by_rate=False)
        fig_age = px.bar(
            age_data, x="AgeGroup", y="AttritionRate(%)",
            text=[f"{r}% (n={n})" for r, n in zip(age_data["AttritionRate(%)"], age_data["Employees"])],
            color="AttritionRate(%)", color_continuous_scale="Reds",
            title="Attrition Rate by Age Group"
        )
        fig_age.update_traces(textposition="outside")
        fig_age.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_age, use_container_width=True)

    with c2:
        # Gender
        gender_data = attrition_by_group(df, "Gender")
        fig_gender = px.bar(
            gender_data, x="Gender", y="AttritionRate(%)",
            text=[f"{r}% (n={n})" for r, n in zip(gender_data["AttritionRate(%)"], gender_data["Employees"])],
            color="Gender", color_discrete_sequence=["#4facfe", "#f093fb"],
            title="Attrition Rate by Gender"
        )
        fig_gender.update_traces(textposition="outside")
        fig_gender.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_gender, use_container_width=True)

    c3, c4 = st.columns(2)

    with c3:
        # Marital Status
        ms_data = attrition_by_group(df, "MaritalStatus")
        fig_ms = px.bar(
            ms_data, x="MaritalStatus", y="AttritionRate(%)",
            text=[f"{r}% (n={n})" for r, n in zip(ms_data["AttritionRate(%)"], ms_data["Employees"])],
            color="AttritionRate(%)", color_continuous_scale="YlOrRd",
            title="Attrition Rate by Marital Status"
        )
        fig_ms.update_traces(textposition="outside")
        fig_ms.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_ms, use_container_width=True)

    with c4:
        # Education Level
        edu_data = attrition_by_group(df, "EducationLabel")
        fig_edu = px.bar(
            edu_data, x="EducationLabel", y="AttritionRate(%)",
            text=[f"{r}% (n={n})" for r, n in zip(edu_data["AttritionRate(%)"], edu_data["Employees"])],
            color="AttritionRate(%)", color_continuous_scale="Blues",
            title="Attrition Rate by Education Level"
        )
        fig_edu.update_traces(textposition="outside")
        fig_edu.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_edu, use_container_width=True)

    # Education Field
    st.subheader("Attrition by Education Field")
    ef_data = attrition_by_group(df, "EducationField")
    fig_ef = px.bar(
        ef_data, x="EducationField", y="AttritionRate(%)",
        text=[f"{r}% (n={n})" for r, n in zip(ef_data["AttritionRate(%)"], ef_data["Employees"])],
        color="AttritionRate(%)", color_continuous_scale="Viridis",
        title="Attrition Rate by Education Field"
    )
    fig_ef.update_traces(textposition="outside")
    fig_ef.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig_ef, use_container_width=True)

# ──────────────────────────────────────────────────────────────
# TAB 4: Tenure & Workload
# ──────────────────────────────────────────────────────────────
with tab4:
    st.subheader("Tenure & Career Stage Analysis")

    c1, c2 = st.columns(2)

    with c1:
        # Tenure Bucket
        tb_data = attrition_by_group(df, "TenureBucket", sort_by_rate=False)
        fig_tb = px.bar(
            tb_data, x="TenureBucket", y="AttritionRate(%)",
            text=[f"{r}% (n={n})" for r, n in zip(tb_data["AttritionRate(%)"], tb_data["Employees"])],
            color="AttritionRate(%)", color_continuous_scale="Reds",
            title="Attrition Rate by Tenure Bucket"
        )
        fig_tb.update_traces(textposition="outside")
        fig_tb.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_tb, use_container_width=True)

    with c2:
        # Career Stage
        cs_data = attrition_by_group(df, "CareerStage")
        fig_cs = px.bar(
            cs_data, x="CareerStage", y="AttritionRate(%)",
            text=[f"{r}% (n={n})" for r, n in zip(cs_data["AttritionRate(%)"], cs_data["Employees"])],
            color="AttritionRate(%)", color_continuous_scale="YlOrRd",
            title="Attrition Rate by Career Stage"
        )
        fig_cs.update_traces(textposition="outside")
        fig_cs.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_cs, use_container_width=True)

    c3, c4 = st.columns(2)

    with c3:
        # Promotion Stagnation
        ps_data = attrition_by_group(df, "PromotionStagnation", sort_by_rate=False)
        fig_ps = px.bar(
            ps_data, x="PromotionStagnation", y="AttritionRate(%)",
            text=[f"{r}% (n={n})" for r, n in zip(ps_data["AttritionRate(%)"], ps_data["Employees"])],
            color="AttritionRate(%)", color_continuous_scale="Oranges",
            title="Attrition Rate by Promotion Stagnation"
        )
        fig_ps.update_traces(textposition="outside")
        fig_ps.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_ps, use_container_width=True)

    with c4:
        # Distance Band
        db_data = attrition_by_group(df, "DistanceBand", sort_by_rate=False)
        fig_db = px.bar(
            db_data, x="DistanceBand", y="AttritionRate(%)",
            text=[f"{r}% (n={n})" for r, n in zip(db_data["AttritionRate(%)"], db_data["Employees"])],
            color="AttritionRate(%)", color_continuous_scale="Purples",
            title="Attrition Rate by Distance from Home"
        )
        fig_db.update_traces(textposition="outside")
        fig_db.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_db, use_container_width=True)

    st.markdown("---")
    st.subheader("Workload Impact Analysis")

    c5, c6 = st.columns(2)

    with c5:
        # OverTime
        ot_data = attrition_by_group(df, "OverTime")
        fig_ot = px.bar(
            ot_data, x="OverTime", y="AttritionRate(%)",
            text=[f"{r}% (n={n})" for r, n in zip(ot_data["AttritionRate(%)"], ot_data["Employees"])],
            color="OverTime", color_discrete_sequence=["#f5576c", "#4facfe"],
            title="Attrition Rate: OverTime Impact"
        )
        fig_ot.update_traces(textposition="outside")
        fig_ot.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_ot, use_container_width=True)

    with c6:
        # Business Travel
        bt_data = attrition_by_group(df, "BusinessTravel")
        fig_bt = px.bar(
            bt_data, x="BusinessTravel", y="AttritionRate(%)",
            text=[f"{r}% (n={n})" for r, n in zip(bt_data["AttritionRate(%)"], bt_data["Employees"])],
            color="AttritionRate(%)", color_continuous_scale="YlOrRd",
            title="Attrition Rate by Business Travel"
        )
        fig_bt.update_traces(textposition="outside")
        fig_bt.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_bt, use_container_width=True)

    # OverTime × BusinessTravel Heatmap
    st.subheader("OverTime × Business Travel — Combined Heatmap")
    ot_bt_pivot = df.pivot_table(
        values="AttritionFlag", index="OverTime", columns="BusinessTravel", aggfunc="mean"
    ) * 100

    fig_ot_bt = px.imshow(
        ot_bt_pivot.round(1),
        text_auto=".1f",
        color_continuous_scale="YlOrRd",
        aspect="auto",
        labels=dict(x="Business Travel", y="OverTime", color="Rate (%)"),
        title="Attrition Rate (%) — OverTime × Business Travel"
    )
    fig_ot_bt.update_layout(height=350)
    st.plotly_chart(fig_ot_bt, use_container_width=True)

# ──────────────────────────────────────────────────────────────
# TAB 5: Insights
# ──────────────────────────────────────────────────────────────
with tab5:
    st.subheader("🔎 Auto-Generated Risk Insights")
    st.markdown(
        "_The following insights are dynamically computed based on your current filter selection._"
    )

    # Collect all segments and their attrition rates
    segments = []

    # By department
    for _, row in attrition_by_group(df, "Department").iterrows():
        segments.append({
            "Segment": f"Department: {row['Department']}",
            "Rate": row["AttritionRate(%)"],
            "N": row["Employees"],
            "Exited": row["Exited"],
        })

    # By job role
    for _, row in attrition_by_group(df, "JobRole").iterrows():
        segments.append({
            "Segment": f"Job Role: {row['JobRole']}",
            "Rate": row["AttritionRate(%)"],
            "N": row["Employees"],
            "Exited": row["Exited"],
        })

    # By age group
    for _, row in attrition_by_group(df, "AgeGroup").iterrows():
        segments.append({
            "Segment": f"Age Group: {row['AgeGroup']}",
            "Rate": row["AttritionRate(%)"],
            "N": row["Employees"],
            "Exited": row["Exited"],
        })

    # By tenure bucket
    for _, row in attrition_by_group(df, "TenureBucket").iterrows():
        segments.append({
            "Segment": f"Tenure: {row['TenureBucket']}",
            "Rate": row["AttritionRate(%)"],
            "N": row["Employees"],
            "Exited": row["Exited"],
        })

    # By marital status
    for _, row in attrition_by_group(df, "MaritalStatus").iterrows():
        segments.append({
            "Segment": f"Marital Status: {row['MaritalStatus']}",
            "Rate": row["AttritionRate(%)"],
            "N": row["Employees"],
            "Exited": row["Exited"],
        })

    # By OverTime
    for _, row in attrition_by_group(df, "OverTime").iterrows():
        segments.append({
            "Segment": f"OverTime: {row['OverTime']}",
            "Rate": row["AttritionRate(%)"],
            "N": row["Employees"],
            "Exited": row["Exited"],
        })

    # By BusinessTravel
    for _, row in attrition_by_group(df, "BusinessTravel").iterrows():
        segments.append({
            "Segment": f"Travel: {row['BusinessTravel']}",
            "Rate": row["AttritionRate(%)"],
            "N": row["Employees"],
            "Exited": row["Exited"],
        })

    # Sort by attrition rate and pick top 3 (with n >= 10 to be meaningful)
    seg_df = pd.DataFrame(segments)
    seg_df = seg_df[seg_df["N"] >= 10].sort_values("Rate", ascending=False).head(3)

    if seg_df.empty:
        st.info("Not enough data to generate insights with the current filters.")
    else:
        for i, (_, row) in enumerate(seg_df.iterrows(), 1):
            low_sample = " ⚠️ *(low sample size)*" if row["N"] < 30 else ""
            delta = row["Rate"] - kpis["overall_rate"]
            direction = "above" if delta > 0 else "below"

            st.markdown(f"""
            ### 🔴 Risk #{i}: **{row['Segment']}**
            - **Attrition Rate**: {row['Rate']}% ({abs(delta):.1f}pp {direction} overall average of {kpis['overall_rate']}%)
            - **Affected Employees**: {int(row['N'])} employees, {int(row['Exited'])} exited{low_sample}
            """)

        st.markdown("---")
        st.markdown("### 📋 Recommended Actions")
        st.markdown("""
        1. **Conduct stay interviews** with employees in the highest-risk segments identified above.
        2. **Review compensation and benefits** for roles and departments with above-average attrition.
        3. **Implement workload management programs** for employees working overtime with frequent travel.
        4. **Strengthen onboarding and mentorship** for early-tenure employees (0-2 years).
        5. **Create career development pathways** for employees with stagnant promotion timelines.
        """)

# ──────────────────────────────────────────────────────────────
# DOWNLOAD BUTTON
# ──────────────────────────────────────────────────────────────
st.sidebar.markdown("---")
st.sidebar.subheader("📥 Export")

@st.cache_data
def convert_to_csv(data):
    return data.to_csv(index=False).encode("utf-8")

csv_download = convert_to_csv(df)
st.sidebar.download_button(
    label="Download Filtered Data (CSV)",
    data=csv_download,
    file_name="filtered_attrition_data.csv",
    mime="text/csv",
)

# Footer
st.sidebar.markdown("---")
st.sidebar.caption(
    "Built for Palo Alto Networks — Workforce Attrition Analysis  \n"
    "Powered by Streamlit & Plotly"
)
