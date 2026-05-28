from pathlib import Path
import duckdb
import pandas as pd

# Processed CSV outputs will go here.
PROCESSED_DIR = Path("data/processed")

# DuckDB database file will go here.
WAREHOUSE_DIR = Path("data/warehouse")
DB_PATH = WAREHOUSE_DIR / "energy_pipeline.duckdb"


def save_processed_outputs(outputs: dict[str, pd.DataFrame]) -> None:
    """
    Save each processed DataFrame as a CSV.

    This is useful for quick inspection and debugging.
    """

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    for table_name, df in outputs.items():
        output_path = PROCESSED_DIR / f"{table_name}.csv"

        # index=False avoids writing pandas' row index into the CSV.
        df.to_csv(output_path, index=False)

        print(f"Saved {output_path}")


def load_to_duckdb(outputs: dict[str, pd.DataFrame]) -> None:
    """
    Load processed DataFrames into DuckDB.

    DuckDB acts like a small local data warehouse for this project.
    In a real company, this might be BigQuery, Snowflake, Redshift or Postgres.
    """

    WAREHOUSE_DIR.mkdir(parents=True, exist_ok=True)

    # Open a connection to the DuckDB database file.
    # If it does not exist yet, DuckDB will create it.
    with duckdb.connect(DB_PATH.as_posix()) as connection:
        for table_name, df in outputs.items():

            # Register the pandas DataFrame as a temporary DuckDB view.
            # This lets DuckDB query the DataFrame directly.
            connection.register("temp_df", df)

            # Create or replace a real DuckDB table from the temporary view.
            connection.execute(
                f"""
                CREATE OR REPLACE TABLE {table_name} AS
                SELECT * FROM temp_df
                """
            )

            # Unregister the temporary view before moving to the next table.
            connection.unregister("temp_df")

            print(f"Loaded table into DuckDB: {table_name}")