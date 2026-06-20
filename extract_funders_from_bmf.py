"""
EcoServants Tech Dev Bonus Script
IRS Business Master File Funder Candidate Extractor

Purpose:
- Load IRS BMF CSV files from a local folder
- Combine records
- Filter likely 501(c)(3) foundations and grantmakers
- Apply a simple fit score
- Export a Grant Tracker-compatible CSV

Usage:
1. Put downloaded IRS BMF CSV files in: data/raw/
2. Run: python scripts/extract_funders_from_bmf.py
3. Review output in: data/output/ecoservants_python_funder_candidates.csv

Notes:
- This is a starter script. Interns may improve it.
- It does not prove a funder accepts applications.
- Strong candidates still need manual review in ProPublica and on official websites.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Iterable

import pandas as pd

# Update this with your EcoServants username or name before submitting.
INTERN_NAME = "intern_username"

RAW_FOLDER = Path("data/raw")
OUTPUT_FOLDER = Path("data/output")
OUTPUT_FILE = OUTPUT_FOLDER / "ecoservants_python_funder_candidates.csv"

FOUNDATION_KEYWORDS = [
    "FOUNDATION",
    "FAMILY FOUNDATION",
    "COMMUNITY FOUNDATION",
    "CHARITABLE FOUNDATION",
    "TRUST",
    "FUND",
    "CHARITABLE",
    "ENDOWMENT",
]

# NTEE first-letter categories that may be relevant to EcoServants.
# C = Environment, D = Animals, O = Youth Development, P = Human Services,
# S = Community Improvement, T = Philanthropy, U = Science/Technology, W = Public Benefit
RELEVANT_NTEE_PREFIXES = ("C", "D", "O", "P", "S", "T", "U", "W")


def first_existing_column(df: pd.DataFrame, candidates: Iterable[str]) -> str | None:
    """Return the first column name that exists in the dataframe."""
    columns = {column.upper(): column for column in df.columns}
    for candidate in candidates:
        if candidate.upper() in columns:
            return columns[candidate.upper()]
    return None


def clean_text(series: pd.Series) -> pd.Series:
    """Normalize text to uppercase strings without changing missing values into 'nan'."""
    return series.fillna("").astype(str).str.strip().str.upper()


def load_bmf_csvs(raw_folder: Path) -> pd.DataFrame:
    """Load all CSV files found recursively under the raw data folder."""
    csv_files = sorted(raw_folder.rglob("*.csv"))

    if not csv_files:
        raise FileNotFoundError(
            f"No CSV files found in {raw_folder.resolve()}. "
            "Place the IRS BMF CSV files in data/raw/ and try again."
        )

    frames = []
    for file in csv_files:
        print(f"Loading: {file}")
        try:
            df = pd.read_csv(file, dtype=str, low_memory=False)
            df["source_file"] = file.name
            frames.append(df)
        except Exception as exc:
            print(f"Skipping {file.name} because it could not be read: {exc}")

    if not frames:
        raise RuntimeError("CSV files were found, but none could be loaded.")

    return pd.concat(frames, ignore_index=True, sort=False)


def score_funder(row: pd.Series, column_map: dict[str, str | None]) -> int:
    """Apply a simple, explainable fit score."""
    score = 0

    name = row.get(column_map["name"], "") if column_map["name"] else ""
    state = row.get(column_map["state"], "") if column_map["state"] else ""
    ntee = row.get(column_map["ntee"], "") if column_map["ntee"] else ""
    asset_code = row.get(column_map["asset"], "") if column_map["asset"] else ""
    income_code = row.get(column_map["income"], "") if column_map["income"] else ""

    if "FOUNDATION" in name:
        score += 30
    if "COMMUNITY FOUNDATION" in name:
        score += 25
    if "FAMILY FOUNDATION" in name:
        score += 20
    if "TRUST" in name:
        score += 20
    if "FUND" in name:
        score += 15
    if "CHARITABLE" in name:
        score += 15
    if state == "CA":
        score += 15
    if ntee.startswith(RELEVANT_NTEE_PREFIXES):
        score += 20
    if asset_code not in ["", "0", "nan", "None", None]:
        score += 10
    if income_code not in ["", "0", "nan", "None", None]:
        score += 10

    return score


def main() -> None:
    OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

    all_records = load_bmf_csvs(RAW_FOLDER)
    print(f"Total records loaded: {len(all_records):,}")

    # IRS BMF files may differ slightly in column casing or names. This map helps the script adapt.
    column_map = {
        "ein": first_existing_column(all_records, ["EIN"]),
        "name": first_existing_column(all_records, ["NAME", "ORGANIZATION_NAME", "ORG_NAME"]),
        "street": first_existing_column(all_records, ["STREET", "ADDRESS", "ADDRESS_LINE_1"]),
        "city": first_existing_column(all_records, ["CITY"]),
        "state": first_existing_column(all_records, ["STATE"]),
        "zip": first_existing_column(all_records, ["ZIP", "ZIP_CODE"]),
        "subsection": first_existing_column(all_records, ["SUBSECTION"]),
        "foundation": first_existing_column(all_records, ["FOUNDATION"]),
        "ntee": first_existing_column(all_records, ["NTEE_CD", "NTEE"]),
        "asset": first_existing_column(all_records, ["ASSET_CD", "ASSET_CODE"]),
        "income": first_existing_column(all_records, ["INCOME_CD", "INCOME_CODE"]),
    }

    required = ["ein", "name"]
    missing_required = [key for key in required if not column_map[key]]
    if missing_required:
        raise ValueError(f"Missing required BMF columns: {missing_required}. Found columns: {list(all_records.columns)}")

    # Normalize core text fields.
    for key in ["name", "city", "state", "ntee", "subsection", "asset", "income"]:
        column = column_map.get(key)
        if column:
            all_records[column] = clean_text(all_records[column])

    # Start with 501(c)(3) if SUBSECTION exists. If not, proceed with name-based filtering.
    if column_map["subsection"]:
        filtered = all_records[all_records[column_map["subsection"]] == "03"].copy()
    else:
        filtered = all_records.copy()

    keyword_pattern = "|".join(FOUNDATION_KEYWORDS)
    filtered = filtered[filtered[column_map["name"]].str.contains(keyword_pattern, na=False)].copy()

    filtered["fit_score"] = filtered.apply(lambda row: score_funder(row, column_map), axis=1)
    filtered = filtered.sort_values("fit_score", ascending=False)

    def col_value(df: pd.DataFrame, key: str, default: str = "") -> pd.Series:
        column = column_map.get(key)
        if column and column in df.columns:
            return df[column].fillna("").astype(str)
        return pd.Series([default] * len(df), index=df.index)

    address = (
        col_value(filtered, "street") + ", " +
        col_value(filtered, "city") + ", " +
        col_value(filtered, "state") + " " +
        col_value(filtered, "zip")
    ).str.strip(" ,")

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    output = pd.DataFrame({
        "title": col_value(filtered, "name"),
        "funder": col_value(filtered, "name"),
        "funder_type": "Possible Foundation / Grantmaker",
        "total_assets": "",
        "total_giving": "",
        "avg_grant_amount": "",
        "median_grant_amount": "",
        "ein": col_value(filtered, "ein"),
        "address": address,
        "phone": "",
        "website": "",
        "contacts": 0,
        "notes": (
            "Identified from IRS Business Master File as a possible funder. "
            "Manual review needed through ProPublica Nonprofit Explorer and official website. Fit score: "
            + filtered["fit_score"].astype(str)
        ),
        "status": "Researching",
        "next_task": "Review ProPublica filing, confirm grantmaking evidence and find official application guidelines",
        "deadline": "",
        "amount": "",
        "mission_keywords": "environment, conservation, sustainability, education, community service, nonprofit support",
        "program_area_keywords": "environmental programs, volunteer service, community improvement, youth education",
        "geographic_focus_keywords": col_value(filtered, "state"),
        "funding_type_keywords": "project grants, program support, capacity building",
        "exclusion_keywords": "unknown",
        "keyword_enriched_by": INTERN_NAME,
        "keyword_enriched_at": now,
    })

    output.to_csv(OUTPUT_FILE, index=False)
    print(f"Potential funder candidates exported: {len(output):,}")
    print(f"Output saved to: {OUTPUT_FILE.resolve()}")


if __name__ == "__main__":
    main()
