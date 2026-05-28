from pathlib import Path

from injest import load_raw_data
from validate import validate_all
from transform import transform_all
from load import save_processed_outputs, load_to_duckdb

# Processed output folder.
PROCESSED_DIR = Path("data/processed")


def main() -> None:
    """
    Run the full pipeline from raw input files to processed warehouse tables.

    Pipeline order:
    1. Load raw data
    2. Validate raw data
    3. Transform data
    4. Save processed CSV outputs
    5. Load processed data into DuckDB
    """

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    print("Step 1: Loading raw data")
    raw_data = load_raw_data()

    print("Step 2: Validating raw data")
    data_quality_issues = validate_all(raw_data)

    # Save the data quality issue report separately so it can be reviewed.
    data_quality_issues.to_csv(
        PROCESSED_DIR / "data_quality_issues.csv",
        index=False,
    )

    print(f"Found {len(data_quality_issues)} data quality issues")

    print("Step 3: Transforming data")
    transformed_outputs = transform_all(raw_data)

    # Include the issue report as one of the processed outputs.
    # This means it will also be saved and loaded into DuckDB.
    transformed_outputs["data_quality_issues"] = data_quality_issues

    print("Step 4: Saving processed outputs")
    save_processed_outputs(transformed_outputs)

    print("Step 5: Loading outputs into DuckDB")
    load_to_duckdb(transformed_outputs)

    print("Pipeline completed successfully")


if __name__ == "__main__":
    main()