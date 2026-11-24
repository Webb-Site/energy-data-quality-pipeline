import pandas as pd

from src.transform import clean_customers, clean_meter_readings


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

def test_later_duplicate_customer_is_removed():
    customers = pd.DataFrame(
        [
            {"customer_id": "C001", "postcode": "e14 3wq ", "signup_date": "2024-01-15", "customer_type": "residential"},
            {"customer_id": "C001", "postcode": "N1 9GU", "signup_date": "2024-02-01", "customer_type": "residential"},
        ]
    )

    cleaned = clean_customers(customers)

    assert len(cleaned) == 1
    assert cleaned.iloc[0]["postcode"] == "E14 3WQ"
