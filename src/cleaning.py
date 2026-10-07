"""
cleaning.py — Data loading, cleaning, and feature engineering for HR Attrition dataset.

Functions:
    load_data(path)        : Load CSV into a DataFrame.
    clean_data(df)         : Validate, deduplicate, standardize, and drop useless columns.
    engineer_features(df)  : Add derived columns (AgeGroup, TenureBucket, etc.).
    prepare_data(path)     : End-to-end pipeline: load → clean → engineer.
"""

import pandas as pd
import numpy as np
from pathlib import Path


# ---------------------------------------------------------------------------
# 1. LOAD
# ---------------------------------------------------------------------------

def load_data(path: str = "data/attrition.csv") -> pd.DataFrame:
    """Load the attrition CSV and return a raw DataFrame."""
    filepath = Path(path)
    if not filepath.exists():
        raise FileNotFoundError(f"Dataset not found at {filepath.resolve()}")
    df = pd.read_csv(filepath)
    print(f"[load_data] Loaded {df.shape[0]} rows × {df.shape[1]} columns from {filepath}")
    return df


# ---------------------------------------------------------------------------
# 2. CLEAN
# ---------------------------------------------------------------------------

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validate and clean the raw DataFrame:
    - Map Attrition Yes/No → 1/0 (new column: AttritionFlag).
    - Strip whitespace and title-case string columns.
    - Drop constant / useless columns (EmployeeCount, StandardHours, Over18, EmployeeNumber).
    - Remove exact duplicate rows.
    - Report null counts.
    """
    df = df.copy()

    # --- Attrition validation & binary flag ---
    # Convert Attrition to string if needed and map Yes/No → 1/0
    df["Attrition"] = df["Attrition"].astype(str).str.strip()
    valid_labels = {"Yes", "No"}
    unexpected = set(df["Attrition"].unique()) - valid_labels
    if unexpected:
        print(f"[clean_data] ⚠ Unexpected Attrition labels found: {unexpected}")
    df["AttritionFlag"] = df["Attrition"].map({"Yes": 1, "No": 0})
    print(f"[clean_data] AttritionFlag created — {df['AttritionFlag'].sum()} leavers "
          f"({df['AttritionFlag'].mean():.1%} attrition rate)")

    # --- Standardize string columns (strip + title-case) ---
    str_cols = ["Department", "EducationField", "Gender", "JobRole",
                "MaritalStatus", "BusinessTravel", "OverTime"]
    for col in str_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.title()
    # Fix BusinessTravel underscores back after title-case
    df["BusinessTravel"] = df["BusinessTravel"].str.replace("_", "-")

    # --- Drop constant / useless columns ---
    drop_cols = ["EmployeeCount", "StandardHours", "Over18", "EmployeeNumber"]
    existing_drops = [c for c in drop_cols if c in df.columns]
    if existing_drops:
        df.drop(columns=existing_drops, inplace=True)
        print(f"[clean_data] Dropped constant columns: {existing_drops}")

    # --- Duplicates ---
    n_dup = df.duplicated().sum()
    if n_dup > 0:
        df.drop_duplicates(inplace=True)
        print(f"[clean_data] Removed {n_dup} duplicate rows")
    else:
        print("[clean_data] No duplicate rows found")

    # --- Nulls ---
    null_counts = df.isnull().sum()
    nulls = null_counts[null_counts > 0]
    if len(nulls) > 0:
        print(f"[clean_data] ⚠ Null values:\n{nulls}")
    else:
        print("[clean_data] No null values found")

    print(f"[clean_data] Cleaned shape: {df.shape[0]} rows × {df.shape[1]} columns")
    return df


# ---------------------------------------------------------------------------
# 3. FEATURE ENGINEERING
# ---------------------------------------------------------------------------

# Readable education labels
EDUCATION_MAP = {
    1: "Below College",
    2: "College",
    3: "Bachelor",
    4: "Master",
    5: "Doctor",
}


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add derived columns for analysis and dashboarding:
    - AgeGroup:             18-25, 26-35, 36-45, 46-55, 56+
    - TenureBucket:         0-2, 3-5, 6-10, 10+ years at company
    - CareerStage:          Early (0-2 yrs), Mid (3-9 yrs), Senior (10+ yrs)
    - DistanceBand:         Near (1-5 km), Medium (6-15 km), Far (16+ km)
    - PromotionStagnation:  0-1, 2-4, 5+ years since last promotion
    - EducationLabel:       Readable education level name
    """
    df = df.copy()

    # Age Group
    bins_age = [17, 25, 35, 45, 55, 100]
    labels_age = ["18-25", "26-35", "36-45", "46-55", "56+"]
    df["AgeGroup"] = pd.cut(df["Age"], bins=bins_age, labels=labels_age)

    # Tenure Bucket (YearsAtCompany)
    bins_tenure = [-1, 2, 5, 10, 50]
    labels_tenure = ["0-2 yrs", "3-5 yrs", "6-10 yrs", "10+ yrs"]
    df["TenureBucket"] = pd.cut(df["YearsAtCompany"], bins=bins_tenure, labels=labels_tenure)

    # Career Stage
    def _career_stage(yac):
        if yac <= 2:
            return "Early"
        elif yac <= 9:
            return "Mid"
        else:
            return "Senior"
    df["CareerStage"] = df["YearsAtCompany"].apply(_career_stage)

    # Distance Band
    bins_dist = [0, 5, 15, 100]
    labels_dist = ["Near (1-5)", "Medium (6-15)", "Far (16+)"]
    df["DistanceBand"] = pd.cut(df["DistanceFromHome"], bins=bins_dist, labels=labels_dist)

    # Promotion Stagnation
    bins_promo = [-1, 1, 4, 100]
    labels_promo = ["0-1 yrs", "2-4 yrs", "5+ yrs"]
    df["PromotionStagnation"] = pd.cut(
        df["YearsSinceLastPromotion"], bins=bins_promo, labels=labels_promo
    )

    # Education Label
    df["EducationLabel"] = df["Education"].map(EDUCATION_MAP).fillna("Unknown")

    print(f"[engineer_features] Added 6 engineered columns — final shape: "
          f"{df.shape[0]} rows × {df.shape[1]} columns")
    return df


# ---------------------------------------------------------------------------
# 4. PIPELINE
# ---------------------------------------------------------------------------

def prepare_data(path: str = "data/attrition.csv") -> pd.DataFrame:
    """End-to-end: load → clean → engineer features."""
    df = load_data(path)
    df = clean_data(df)
    df = engineer_features(df)
    return df


# ---------------------------------------------------------------------------
# Quick test when run directly
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    df = prepare_data()
    print("\n--- Sample ---")
    print(df[["Age", "AgeGroup", "Department", "JobRole", "AttritionFlag",
              "TenureBucket", "CareerStage", "DistanceBand",
              "PromotionStagnation", "EducationLabel"]].head(10))
    print(f"\nEngineered columns: {[c for c in df.columns if c in ['AgeGroup','TenureBucket','CareerStage','DistanceBand','PromotionStagnation','EducationLabel','AttritionFlag']]}")
