# Energy Data Quality Pipeline

A small Python and SQL data pipeline that ingests energy customer, tariff and meter-reading data, validates common data quality issues, transforms the data into reporting-ready outputs, and loads the results into DuckDB.

The project is intentionally small, but structured around production-minded habits: modular code, reusable validation helpers, data quality reporting, automated tests, clear documentation and a local analytical warehouse layer.

---

## Why I built this

I built this project to practise data platform engineering concepts relevant to energy data, including:

- data ingestion
- schema and business-rule validation
- data quality reporting
- cleaning and transformation
- reporting-ready dataset design
- local warehouse loading
- SQL quality checks
- automated testing
- documentation and maintainable project structure

The project is also part of my move from BI/reporting and workflow automation toward analytics engineering, data engineering and data platform work.

---

## Pipeline flow

```text
Raw CSV files
→ Python ingestion
→ schema and data quality validation
→ cleaning and transformation
→ reporting-ready monthly usage summary
→ DuckDB local warehouse
→ SQL checks and pytest tests
```

---

## Project structure

```text
energy-data-quality-pipeline/
  data/
    raw/              # source CSV files before cleaning
    processed/        # cleaned outputs and data quality report
    warehouse/        # local DuckDB database
  src/
    __init__.py
    make_sample_data.py
    ingest.py
    validate.py
    transform.py
    load.py
    run_pipeline.py
  sql/
    data_quality_checks.sql
  tests/
    test_validate.py
    test_transform.py
  docs/
  README.md
  requirements.txt
  pyproject.toml
```

---

## What it demonstrates

- Python data processing with pandas
- Modular pipeline design
- Reusable validation logic
- Data quality issue reporting
- SQL-based data quality checks
- DuckDB local warehouse usage
- Reporting-ready dataset creation
- Automated tests with pytest
- Basic package-style Python imports
- Maintainability and refactoring decisions

---

## Data quality checks

The validation layer checks for:

- missing required columns
- missing customer postcodes
- invalid customer signup dates
- duplicate customer IDs
- invalid meter-reading timestamps
- negative kWh readings
- unusually high kWh readings
- meter readings linked to unknown customers
- missing or invalid tariff unit rates

Duplicate customer handling is deliberate: the pipeline treats the first occurrence of a `customer_id` as the accepted record and flags later occurrences as duplicate records. Later duplicate rows are excluded from the cleaned customer output.

In a production setting, this rule would need to be agreed with data owners. For example, a source-system timestamp such as `updated_at` might be used to decide whether the first or latest record should be treated as correct.

---

## Main outputs

The pipeline creates:

```text
data/processed/clean_customers.csv
data/processed/clean_meter_readings.csv
data/processed/clean_tariffs.csv
data/processed/monthly_usage_summary.csv
data/processed/data_quality_issues.csv
data/warehouse/energy_pipeline.duckdb
```

---

## `data_quality_issues.csv`

A structured report of detected data quality issues.

Example columns:

```text
source_file
row_id
field
issue_type
issue_description
```

Example issues include:

```text
missing_value
invalid_date
invalid_value
duplicate_record
orphan_record
outlier
```

This makes data quality issues queryable and auditable rather than just printing errors to the console.

---

## `monthly_usage_summary.csv`

A reporting-ready table summarising customer energy usage by month.

Example columns:

```text
customer_id
postcode
customer_type
reading_month
tariff_name
total_kwh
average_kwh_per_reading
estimated_cost
reading_count
```

This is the type of cleaned, aggregated table that could support a dashboard, analyst workflow or downstream reporting layer.

---

## How to run

Create and activate a virtual environment:

```bash
python -m venv .venv
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Generate sample raw data:

```bash
python -m src.make_sample_data
```

Run the pipeline:

```bash
python -m src.run_pipeline
```

Run tests:

```bash
python -m pytest
```

---

## Testing

The project uses `pytest` to test key validation and transformation behaviour.

Current tests cover:

- negative kWh readings are flagged
- orphan meter readings are flagged
- missing tariff rates are flagged
- invalid reading dates are removed
- later duplicate customer records are flagged
- later duplicate customer records are removed from cleaned outputs
- unusually high kWh readings are flagged as outliers

Passing tests confirm that the core validation and cleaning rules behave as expected.

---

## Design decisions

### Reusable required-column validation

The validation layer uses a reusable helper function to check whether each dataset contains the required columns. This avoids repeating the same schema-checking logic across customers, meter readings and tariffs.

### Structured issue reporting

Validation issues are collected into a structured DataFrame and saved as `data_quality_issues.csv`. This makes data quality issues easier to inspect, query, track and potentially dashboard.

### Validation and transformation are separate

Validation identifies and reports data quality issues.

Transformation decides how records should be cleaned for downstream use.

For example, duplicate customer records are flagged during validation, and later duplicate records are then removed during cleaning.

### Duplicate handling

For customer records, the first occurrence of a `customer_id` is treated as the accepted record. Later occurrences are flagged as duplicates and removed from the cleaned customer output.

This is a simple rule for this project. In production, duplicate-handling logic would need to be agreed with data owners and could depend on timestamps, source-system priority, or manual review workflows.

### Column selection before copying

Cleaning functions select only the columns needed downstream before copying the data. This is more memory-conscious than copying entire raw DataFrames, especially if source files become wider over time.

For larger datasets, I would look to push more transformations into SQL, DuckDB, BigQuery or another warehouse-style engine rather than relying on full in-memory pandas copies.

### DuckDB as a local warehouse

DuckDB is used as a lightweight local analytical database. It gives the project a simple warehouse layer without requiring cloud infrastructure.

In a production system, this could be replaced by BigQuery, Snowflake, Postgres, Databricks or another managed data platform.

---

## What I would improve in production

If this were developed into a production-style data platform workflow, I would add:

- real public energy/smart meter data ingestion
- API ingestion from carbon intensity or energy system data sources
- orchestration with Airflow, Dagster or Prefect
- cloud warehouse storage such as BigQuery, Snowflake or Postgres
- dbt models for SQL transformations, tests and documentation
- schema validation with pandera or Great Expectations
- CI/CD using GitHub Actions
- monitoring and alerting for failed pipeline runs
- incremental loading rather than full refreshes
- dashboarding in Power BI, Lightdash or Looker Studio
- clearer data ownership and agreed business rules for duplicate handling

---

## Summary

This project is a small but complete example of a data quality pipeline.

It shows how raw operational energy data can be ingested, validated, cleaned, transformed into reporting-ready outputs and loaded into a queryable local warehouse.

The main focus is not the size of the dataset, but the engineering habits behind it:

- modular code
- validation
- testing
- documentation
- data quality visibility
- maintainable pipeline design
- thinking about how local pipeline logic could evolve into production data platform work