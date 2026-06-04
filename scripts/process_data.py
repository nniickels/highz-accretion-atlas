## This code uses functions defined in src/standardize_data.py to generate a standardized CSV file.
## It rewrites the processed CSV from the current raw CSV each run so newly appended raw rows
## from additional papers are always propagated into the processed file.

# ---------------------------------- Imports -----------------------------------------------------

from __future__ import annotations
from pathlib import Path
import pandas as pd

from src.standardize_data import standardize_raw_csv

# ------------------------------ Path configuration ---------------------------------------------
 
PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = PROJECT_ROOT / "data" / "raw" / "v1_raw.csv"
PROCESSED_PATH = PROJECT_ROOT / "data" / "processed" / "v1_processed.csv"

# Optional canonical_name -> source_column_name mapping for non-canonical raw tables.
# Leave empty for v1_raw.csv because it already uses canonical names.
COLUMN_MAP: dict[str, str] = {}

# ----------------------------------- Script -----------------------------------------------------

def main() -> None:
    """Standardize current raw CSV and overwrite processed CSV."""
    raw_df = pd.read_csv(RAW_PATH)
    standardized_df = standardize_raw_csv(RAW_PATH, column_map=COLUMN_MAP)

    PROCESSED_PATH.parent.mkdir(parents=True, exist_ok=True)
    standardized_df.to_csv(PROCESSED_PATH, mode="w", index=False)
    print(f"Read {len(raw_df)} raw rows: {RAW_PATH}")
    print("Applied v1 redshift filter: redshift >= 4")
    print(f"Wrote {len(standardized_df)} standardized rows: {PROCESSED_PATH}")
    print("Optional missing-field counts after filtering:")
    for col in ["missing_mstar_flag", "missing_lbol_flag", "missing_edd_ratio_flag", "missing_lensing_flag"]:
        print(f"  {col}: {int(standardized_df[col].sum())}")

if __name__ == "__main__":               # enter "python -m scripts.process_data" in terminal
    main()
