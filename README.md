# Energy Data Quality Pipeline

## Summary
A small Python and SQL data pipeline that ingests messy energy customer and meter-reading data, validates it, transforms it into reporting-ready tables, and produces a data quality report.

## Why I built this
I built this as a focused project to practise data platform engineering concepts relevant to energy data: ingestion, validation, transformation, testing, documentation and reliable reporting outputs.

## Architecture
Raw CSV files → Python ingestion → validation checks → cleaned datasets → SQLite/DuckDB tables → SQL quality checks → reporting-ready monthly summary

## What it demonstrates
- Python data processing
- SQL data quality checks
- validation and reconciliation logic
- clean project structure
- testing with pytest
- documentation and data dictionaries
- energy-domain thinking

## How to run
```bash
pip install -r requirements.txt
python src/run_pipeline.py
pytest