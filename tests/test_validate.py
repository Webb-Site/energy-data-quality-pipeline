import pandas as pd

from src.validate import validate_meter_readings, validate_tariffs


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