import pandas as pd


def clean_customers(customers: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the customers table.

    We standardise the postcode, parse signup_date into a real date,
    and remove rows that cannot be used safely downstream.
    """

    # Thinking ahead, for larger datasets I may encounter memory issues if I keep unnecessary columns around.
    columns_needed = ["customer_id", "postcode", "signup_date", "customer_type"]
    
    # Work on a copy so we do not accidentally modify the original raw data.
    df = customers[columns_needed].copy()

    # Convert signup_date from text into a datetime column.
    # Invalid dates become NaT.
    df["signup_date"] = pd.to_datetime(df["signup_date"], errors="coerce")

    # Standardise postcode formatting:
    # - fill missing values with blank string
    # - uppercase everything
    # - remove leading/trailing spaces
    df["postcode"] = df["postcode"].fillna("").str.upper().str.strip()
    
    # Remove Duplicate Customers
    df = df.drop_duplicates(subset="customer_id", keep="first")

    # Keep only rows with a customer_id and a valid signup date.
    # This is a simple cleaning choice for the project.
    df = df[
        df["customer_id"].notna()
        & df["signup_date"].notna()
    ]

    return df


def clean_meter_readings(
    meter_readings: pd.DataFrame,
    customers: pd.DataFrame,
) -> pd.DataFrame:
    """
    Clean meter readings.

    We remove readings with invalid timestamps, negative usage,
    or customer IDs that do not exist in the cleaned customers table.
    """
    
    columns_needed = ["reading_id", "customer_id", "reading_start", "kwh_used"]

    df = meter_readings[columns_needed].copy()

    # Convert reading_start from text into a timezone-aware timestamp.
    df["reading_start"] = pd.to_datetime(
        df["reading_start"],
        errors="coerce",
        utc=True,
    )

    # Remove rows where the timestamp could not be parsed.
    df = df[df["reading_start"].notna()]

    # Remove rows with negative energy usage.
    df = df[df["kwh_used"] >= 0]

    # Keep only readings linked to known cleaned customers.
    df = df[df["customer_id"].isin(set(customers["customer_id"]))]

    # Create useful date fields for reporting.
    # reading_date supports daily analysis.
    # reading_month supports monthly summaries.
    df["reading_date"] = df["reading_start"].dt.date
    df["reading_month"] = df["reading_start"].dt.to_period("M").astype(str)

    return df


def clean_tariffs(tariffs: pd.DataFrame) -> pd.DataFrame:
    """
    Clean tariff data.

    We only keep tariffs with valid positive unit rates because otherwise
    estimated cost cannot be calculated reliably.
    """

    columns_needed = ["customer_id", "tariff_name", "unit_rate"]
    df = tariffs[columns_needed].copy()

    # Remove missing rates.
    df = df[df["unit_rate"].notna()]

    # Remove zero or negative rates.
    df = df[df["unit_rate"] > 0]

    return df


def build_monthly_usage_summary(
    meter_readings: pd.DataFrame,
    customers: pd.DataFrame,
    tariffs: pd.DataFrame,
) -> pd.DataFrame:
    """
    Build the main reporting-ready output table.

    This joins readings to customer and tariff information, then aggregates
    usage and estimated cost by customer and month.
    """

    # Join meter readings to customers so each reading has customer context.
    # how="left" means keep all meter readings, even if customer details are missing.
    enriched = meter_readings.merge(
        customers[["customer_id", "postcode", "customer_type"]],
        on="customer_id",
        how="left",
    )

    # Join tariff information so we can calculate estimated cost.
    enriched = enriched.merge(
        tariffs[["customer_id", "tariff_name", "unit_rate"]],
        on="customer_id",
        how="left",
    )

    # Derived metric:
    # estimated cost = electricity used multiplied by tariff unit rate.
    enriched["estimated_cost"] = enriched["kwh_used"] * enriched["unit_rate"]

    # Aggregate readings into a monthly customer-level summary.
    # This is the kind of table that could feed a dashboard.
    monthly_summary = (
        enriched
        .groupby(
            [
                "customer_id",
                "postcode",
                "customer_type",
                "reading_month",
                "tariff_name",
            ],
            dropna=False,
        )
        .agg(
            total_kwh=("kwh_used", "sum"),
            estimated_cost=("estimated_cost", "sum"),
            reading_count=("reading_id", "count"),
        )
        .reset_index()
    )

    return monthly_summary


def transform_all(raw_data: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    """
    Run all transformation steps and return processed datasets.

    Returning a dictionary keeps the outputs named and easy to load later.
    """

    clean_customer_data = clean_customers(raw_data["customers"])

    clean_reading_data = clean_meter_readings(
        raw_data["meter_readings"],
        clean_customer_data,
    )

    clean_tariff_data = clean_tariffs(raw_data["tariffs"])

    monthly_usage_summary = build_monthly_usage_summary(
        clean_reading_data,
        clean_customer_data,
        clean_tariff_data,
    )

    return {
        "clean_customers": clean_customer_data,
        "clean_meter_readings": clean_reading_data,
        "clean_tariffs": clean_tariff_data,
        "monthly_usage_summary": monthly_usage_summary,
    }