import pandas as pd


def add_issue(
    issues: list[dict],
    source_file: str,
    row_id: str,
    field: str,
    issue_type: str,
    issue_description: str,
) -> None:
    """
    Add one data quality issue to the issues list.

    Instead of just printing errors, we store issues in a structured format.
    This makes them easy to save as a CSV, query later, or display in a dashboard.
    """

    issues.append(
        {
            "source_file": source_file,
            "row_id": row_id,
            "field": field,
            "issue_type": issue_type,
            "issue_description": issue_description,
        }
    )


def validate_customers(customers: pd.DataFrame) -> list[dict]:
    """
    Validate the customers dataset.

    This checks:
    - expected columns exist
    - postcode is present
    - signup_date can be parsed as a date
    """

    issues = []

    # Define the schema we expect.
    # If any of these columns are missing, downstream code may break.
    required_columns = {"customer_id", "postcode", "signup_date", "customer_type"}

    # Compare expected columns against actual columns in the DataFrame.
    missing_columns = required_columns - set(customers.columns)

    for column in missing_columns:
        add_issue(
            issues,
            "customers",
            "file",
            column,
            "missing_column",
            f"Missing required column: {column}",
        )

    # If required columns are missing, stop validation for this dataset.
    # Otherwise later checks may fail because they depend on those columns.
    if missing_columns:
        return issues

    # Check for blank or missing postcodes.
    missing_postcodes = customers[
        customers["postcode"].isna()
        | (customers["postcode"].astype(str).str.strip() == "")
    ]

    for _, row in missing_postcodes.iterrows():
        add_issue(
            issues,
            "customers",
            row["customer_id"],
            "postcode",
            "missing_value",
            "Customer postcode is missing",
        )

    duplicate_customer_ids = customers[
        customers["customer_id"].duplicated(keep="first")]
    
    for row_index, row in duplicate_customer_ids.iterrows():
        add_issue(
            issues=issues,
            source_file="customers",
            row_id=f"{row['customer_id']} at row {row_index}",
            field="customer_id",
            issue_type="duplicate_record",
            issue_description=(
                "Duplicate customer_id found after first occurrence; "
                "first occurrence is treated as the accepted record"
            ),
        )
    
    # Convert signup_date to a real date.
    # errors="coerce" means invalid dates become NaT instead of crashing.
    parsed_dates = pd.to_datetime(customers["signup_date"], errors="coerce")

    # Any rows where parsing failed are invalid.
    invalid_dates = customers[parsed_dates.isna()]

    for _, row in invalid_dates.iterrows():
        add_issue(
            issues,
            "customers",
            row["customer_id"],
            "signup_date",
            "invalid_date",
            "Signup date could not be parsed",
        )

    return issues


def validate_meter_readings(
    meter_readings: pd.DataFrame,
    customers: pd.DataFrame,
) -> list[dict]:
    """
    Validate the meter readings dataset.

    This checks:
    - expected columns exist
    - reading_start is a valid timestamp
    - kWh usage is not negative
    - each reading belongs to a known customer
    """

    issues = []

    required_columns = {"reading_id", "customer_id", "reading_start", "kwh_used"}
    missing_columns = required_columns - set(meter_readings.columns)

    for column in missing_columns:
        add_issue(
            issues,
            "meter_readings",
            "file",
            column,
            "missing_column",
            f"Missing required column: {column}",
        )

    if missing_columns:
        return issues

    # Parse reading_start into timestamps.
    # utc=True means all timestamps are treated consistently in UTC.
    parsed_dates = pd.to_datetime(
        meter_readings["reading_start"],
        errors="coerce",
        utc=True,
    )

    invalid_dates = meter_readings[parsed_dates.isna()]

    for _, row in invalid_dates.iterrows():
        add_issue(
            issues,
            "meter_readings",
            row["reading_id"],
            "reading_start",
            "invalid_date",
            "Reading start could not be parsed",
        )

    # Energy usage should never be negative.
    # If it is, this could break reporting or billing-style calculations.
    negative_usage = meter_readings[meter_readings["kwh_used"] < 0]

    for _, row in negative_usage.iterrows():
        add_issue(
            issues,
            "meter_readings",
            row["reading_id"],
            "kwh_used",
            "invalid_value",
            "kWh usage cannot be negative",
        )

    # Referential integrity check:
    # every meter reading customer_id should exist in the customers table.
    known_customer_ids = set(customers["customer_id"])

    orphan_readings = meter_readings[
        ~meter_readings["customer_id"].isin(known_customer_ids)
    ]

    for _, row in orphan_readings.iterrows():
        add_issue(
            issues,
            "meter_readings",
            row["reading_id"],
            "customer_id",
            "orphan_record",
            "Meter reading references an unknown customer",
        )

    return issues


def validate_tariffs(tariffs: pd.DataFrame) -> list[dict]:
    """
    Validate the tariffs dataset.

    This checks:
    - expected columns exist
    - unit_rate is present
    - unit_rate is positive
    """

    issues = []

    required_columns = {"customer_id", "tariff_name", "unit_rate"}
    missing_columns = required_columns - set(tariffs.columns)

    for column in missing_columns:
        add_issue(
            issues,
            "tariffs",
            "file",
            column,
            "missing_column",
            f"Missing required column: {column}",
        )

    if missing_columns:
        return issues

    # If unit_rate is missing, estimated cost cannot be calculated.
    missing_rates = tariffs[tariffs["unit_rate"].isna()]

    for _, row in missing_rates.iterrows():
        add_issue(
            issues,
            "tariffs",
            row["customer_id"],
            "unit_rate",
            "missing_value",
            "Tariff unit rate is missing",
        )

    # Unit rates should be positive.
    invalid_rates = tariffs[
        tariffs["unit_rate"].notna()
        & (tariffs["unit_rate"] <= 0)
    ]

    for _, row in invalid_rates.iterrows():
        add_issue(
            issues,
            "tariffs",
            row["customer_id"],
            "unit_rate",
            "invalid_value",
            "Tariff unit rate must be positive",
        )

    return issues


def validate_all(raw_data: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Run all validation checks and return one combined issue report.

    The output is a DataFrame because we want to save/query/report on the issues.
    """

    issues = []

    issues.extend(validate_customers(raw_data["customers"]))

    issues.extend(
        validate_meter_readings(
            raw_data["meter_readings"],
            raw_data["customers"],
        )
    )

    issues.extend(validate_tariffs(raw_data["tariffs"]))

    return pd.DataFrame(
        issues,
        columns=[
            "source_file",
            "row_id",
            "field",
            "issue_type",
            "issue_description",
        ],
    )