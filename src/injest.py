from pathlib import Path
import pandas as pd

# Raw source files live here.
RAW_DIR = Path("data/raw")


def read_csv_file(filename: str) -> pd.DataFrame:
    """
    Read one CSV file from the raw data folder.

    This function gives us one reusable way to load CSV files.
    It also checks that the file exists before trying to read it.
    """

    path = RAW_DIR / filename

    # Fail early with a clear error if the file is missing.
    # This is better than getting a confusing pandas error later.
    if not path.exists():
        raise FileNotFoundError(f"Could not find input file: {path}")

    # Read the CSV into a pandas DataFrame.
    # A DataFrame is like a table in Python: rows and columns.
    df = pd.read_csv(path)

    # Simple logging so we know what has loaded.
    print(f"Loaded {filename}: {len(df)} rows")

    return df


def load_raw_data() -> dict[str, pd.DataFrame]:
    """
    Load all raw input files needed by the pipeline.

    Returning a dictionary makes it easy to pass all datasets between pipeline
    stages using clear names like raw_data["customers"].
    """

    return {
        "customers": read_csv_file("customers.csv"),
        "meter_readings": read_csv_file("meter_readings.csv"),
        "tariffs": read_csv_file("tariffs.csv"),
    }