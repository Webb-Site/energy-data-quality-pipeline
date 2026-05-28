import pandas as pd

from src.transform import clean_meter_readings


def test_invalid_reading_dates_are_removed():
    meter_readings = pd.DataFrame(
        [
            {
                "reading_id": "R001",
                "customer_id": "C001",
                "reading_start": "not_a_date",
                "kwh_used": 1.0,
            },
            {
                "reading_id": "R002",
                "customer_id": "C001",
                "reading_start": "2024-05-01T00:00:00Z",
                "kwh_used": 1.0,
            },
        ]
    )

    customers = pd.DataFrame(
        [
            {"customer_id": "C001"}
        ]
    )

    cleaned = clean_meter_readings(meter_readings, customers)

    assert len(cleaned) == 1
    assert cleaned.iloc[0]["reading_id"] == "R002"