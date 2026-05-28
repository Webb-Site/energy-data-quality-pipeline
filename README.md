# Energy Data Quality Pipeline

A small Python and SQL data pipeline that ingests energy customer, tariff and meter-reading data, validates common data quality issues, transforms the data into reporting-ready outputs, and loads the results into DuckDB.

## Why I built this

I built this project to practise data platform engineering concepts relevant to energy data: ingestion, validation, transformation, testing, documentation and reliable reporting outputs.

The project is intentionally small, but structured around production-minded habits such as modular code, validation checks, automated tests and clear documentation.

## Pipeline flow

Raw CSV files  
→ Python ingestion  
→ data validation  
→ cleaning and transformation  
→ reporting-ready monthly usage summary  
→ DuckDB local warehouse  
→ SQL checks and tests

## What it demonstrates

- Python data processing
- SQL data quality checks
- data validation and reconciliation thinking
- reporting-ready dataset design
- DuckDB local warehouse usage
- automated tests with pytest
- maintainable project structure

## How to run

```bash
pip install -r requirements.txt
python src/make_sample_data.py
python src/run_pipeline.py
pytest