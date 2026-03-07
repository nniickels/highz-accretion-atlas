## This code uses functions defined in src/standardize_data.py to generate a standardized catalogue 
## into an empty csv given a raw data csv file (only the path configuration changes between versions)

# ---------------------------------- Imports -----------------------------------------------------

from __future__ import annotations
from pathlib import Path
import sys
import pandas as pd
from src.standardize_data import standardize_raw_csv    

# ------------------------------ Path configuration ---------------------------------------------
 
RAW_PATH = Path(f"data/raw/v1_raw.csv")                          # path to input csv
PROCESSED_PATH = Path(f"data/processed/v1_processed.csv")        # path to output csv 

# ----------------------------------- Script -----------------------------------------------------

def _processed_csv_is_empty(path: Path) -> bool:
    """Return True when `path` is missing, zero-byte, or has zero data rows."""
    if not path.exists() or path.stat().st_size == 0:
        return True

    try:
        existing = pd.read_csv(path)
    except pd.errors.EmptyDataError:
        return True

    return existing.empty


def main() -> None:
    """Standardize raw data and append to processed CSV only when it is empty."""
    standardized_df = standardize_raw_csv(RAW_PATH)

    PROCESSED_PATH.parent.mkdir(parents=True, exist_ok=True)

    if _processed_csv_is_empty(PROCESSED_PATH):
        standardized_df.to_csv(PROCESSED_PATH, mode="a", index=False)
        print(f"Appended {len(standardized_df)} rows to empty file: {PROCESSED_PATH}")
    else:
        print(f"Skipped write; processed file already has rows: {PROCESSED_PATH}")


if __name__ == "__main__":               # enter "python -m scripts.generate_catalogue" in terminal                       
    main()
