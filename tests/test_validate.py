import pandas as pd

from src.validate import validate_customers, validate_meter_readings, validate_tariffs


def test_negative_kwh_is_flagged():
    meter_readings = pd.DataFrame(
        [
            {
                "reading_id": "R001",
                "customer_id": "C001",
                "reading_start": "2024-05-01T00:00:00Z",
                "kwh_used": -1.0,
            }
        ]
    )

    customers = pd.DataFrame(
        [
            {"customer_id": "C001"}
        ]
    )

    issues = validate_meter_readings(meter_readings, customers)

    assert any(issue["issue_type"] == "invalid_value" for issue in issues)


def test_orphan_meter_reading_is_flagged():
    meter_readings = pd.DataFrame(
        [
            {
                "reading_id": "R001",
                "customer_id": "C999",
                "reading_start": "2024-05-01T00:00:00Z",
                "kwh_used": 1.0,
            }
        ]
    )

    customers = pd.DataFrame(
        [
            {"customer_id": "C001"}
        ]
    )

    issues = validate_meter_readings(meter_readings, customers)

    assert any(issue["issue_type"] == "orphan_record" for issue in issues)


def test_missing_tariff_rate_is_flagged():
    tariffs = pd.DataFrame(
        [
            {
                "customer_id": "C001",
                "tariff_name": "standard",
                "unit_rate": None,
            }
        ]
    )

    issues = validate_tariffs(tariffs)

    assert any(issue["issue_type"] == "missing_value" for issue in issues)

def test_unusually_high_kwh_is_flagged_as_outlier():
    meter_readings = pd.DataFrame(
        [
            {
                "reading_id": "R001",
                "customer_id": "C001",
                "reading_start": "2024-05-01T00:00:00Z",
                "kwh_used": 25.0,
            },
            {
                "reading_id": "R002",
                "customer_id": "C001",
                "reading_start": "2024-05-01T00:30:00Z",
                "kwh_used": 0.3,
            },
        ]
    )

    customers = pd.DataFrame(
        [
            {"customer_id": "C001"}
        ]
    )

    issues = validate_meter_readings(meter_readings, customers)

    outliers = [issue for issue in issues if issue["issue_type"] == "outlier"]
    assert [issue["row_id"] for issue in outliers] == ["R001"]


def test_later_duplicate_customer_is_flagged():
    customers = pd.DataFrame(
        [
            {"customer_id": "C001", "postcode": "E14 3WQ", "signup_date": "2024-01-15", "customer_type": "residential"},
            {"customer_id": "C001", "postcode": "N1 9GU", "signup_date": "2024-02-01", "customer_type": "residential"},
        ]
    )

    issues = validate_customers(customers)

    duplicates = [issue for issue in issues if issue["issue_type"] == "duplicate_record"]
    assert len(duplicates) == 1
