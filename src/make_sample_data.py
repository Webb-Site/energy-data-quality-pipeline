from pathlib import Path
import pandas as pd

# This is where our raw source files will be stored.
# "Raw" means: data as received, before cleaning or transformation.
RAW_DIR = Path("data/raw")


def make_sample_data() -> None:
    """
    Create small sample CSV files for the pipeline.

    In a real project, these files might come from APIs, databases, SFTP folders,
    or external providers. Here, we create them ourselves so we can control the
    data quality issues and practise handling them.
    """

    # Ensure the raw data folder exists before trying to write files into it.
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    # Customer reference data.
    # This is like a dimension/reference table: one row per customer.
    customers = pd.DataFrame(
        [
            {
                "customer_id": "C001",
                "postcode": "E14 3WQ",
                "signup_date": "2024-01-15",
                "customer_type": "residential",
            },
            {
                "customer_id": "C002",
                "postcode": "SW1A 1AA",
                "signup_date": "2024-02-02",
                "customer_type": "residential",
            },
            {
                "customer_id": "C003",
                "postcode": "N1 9GU",
                "signup_date": "2024-03-11",
                "customer_type": "business",
            },
            {
                # Intentional data quality issue:
                # this customer has a missing postcode.
                "customer_id": "C004",
                "postcode": "",
                "signup_date": "2024-04-20",
                "customer_type": "residential",
            },
            {
                # Intentional data quality issue:
                # this signup_date is not a valid date.
                "customer_id": "C005",
                "postcode": "E1 6AN",
                "signup_date": "invalid_date",
                "customer_type": "residential",
            },
        ]
    )

    # Meter readings.
    # This is event/transaction-style data: one row per reading.
    meter_readings = pd.DataFrame(
        [
            {
                "reading_id": "R001",
                "customer_id": "C001",
                "reading_start": "2024-05-01T00:00:00Z",
                "kwh_used": 0.22,
            },
            {
                "reading_id": "R002",
                "customer_id": "C001",
                "reading_start": "2024-05-01T00:30:00Z",
                "kwh_used": 0.18,
            },
            {
                "reading_id": "R003",
                "customer_id": "C002",
                "reading_start": "2024-05-01T00:00:00Z",
                "kwh_used": 0.31,
            },
            {
                "reading_id": "R004",
                "customer_id": "C003",
                "reading_start": "2024-05-01T00:00:00Z",
                "kwh_used": 1.40,
            },
            {
                # Intentional data quality issue:
                # C999 does not exist in customers.csv.
                # This is called an orphan record.
                "reading_id": "R005",
                "customer_id": "C999",
                "reading_start": "2024-05-01T00:00:00Z",
                "kwh_used": 0.25,
            },
            {
                # Intentional data quality issue:
                # energy usage cannot be negative.
                "reading_id": "R006",
                "customer_id": "C004",
                "reading_start": "2024-05-01T00:00:00Z",
                "kwh_used": -0.10,
            },
            {
                # Intentional data quality issue:
                # this reading_start is not a valid timestamp.
                "reading_id": "R007",
                "customer_id": "C005",
                "reading_start": "not_a_date",
                "kwh_used": 0.75,
            },
        ]
    )

    # Tariff data.
    # This tells us how much each customer pays per kWh.
    tariffs = pd.DataFrame(
        [
            {"customer_id": "C001", "tariff_name": "standard", "unit_rate": 0.29},
            {"customer_id": "C002", "tariff_name": "green", "unit_rate": 0.31},
            {"customer_id": "C003", "tariff_name": "business", "unit_rate": 0.27},
            {"customer_id": "C004", "tariff_name": "standard", "unit_rate": 0.29},
            {
                # Intentional data quality issue:
                # missing unit_rate means we cannot calculate estimated cost.
                "customer_id": "C005",
                "tariff_name": "green",
                "unit_rate": None,
            },
        ]
    )

    # Save each DataFrame as a CSV in the raw data folder.
    # index=False avoids writing pandas' row numbers into the CSV.
    customers.to_csv(RAW_DIR / "customers.csv", index=False)
    meter_readings.to_csv(RAW_DIR / "meter_readings.csv", index=False)
    tariffs.to_csv(RAW_DIR / "tariffs.csv", index=False)

    print("Sample data created in data/raw")


# This means: only run make_sample_data() if this file is executed directly.
# If another file imports this one, it will not automatically create data.
if __name__ == "__main__":
    make_sample_data()