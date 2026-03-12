## This code uses functions defined in src/standardize_data.py to generate a standardized CSV file.
## It rewrites the processed CSV from the current raw CSV each run so newly appended raw rows
## from additional papers are always propagated into the processed file.

# ---------------------------------- Imports -----------------------------------------------------

from __future__ import annotations
from pathlib import Path
from src.standardize_data import standardize_raw_csv    

# ------------------------------ Path configuration ---------------------------------------------
 
RAW_PATH = Path(f"data/raw/v1_raw.csv")                          # path to input CSV
PROCESSED_PATH = Path(f"data/processed/v1_processed.csv")        # path to output CSV 

# Optional canonical_name -> source_column_name mapping for non-canonical raw tables.
# Leave empty for v1_raw.csv because it already uses canonical names.
COLUMN_MAP: dict[str, str] = {}

# ----------------------------------- Script -----------------------------------------------------

def main() -> None:
    """Standardize current raw CSV and overwrite processed CSV."""
    standardized_df = standardize_raw_csv(RAW_PATH, column_map=COLUMN_MAP)

    PROCESSED_PATH.parent.mkdir(parents=True, exist_ok=True)
    standardized_df.to_csv(PROCESSED_PATH, mode="w", index=False)
    print(f"Wrote {len(standardized_df)} standardized rows: {PROCESSED_PATH}")

if __name__ == "__main__":               # enter "python -m scripts.process_data" in terminal
    main()