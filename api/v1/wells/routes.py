"""Rutas relacionadas con operaciones de wells."""

from fastapi import APIRouter, Depends
from api.v1.security import get_api_key
from datetime import date
from prometheus_client import Counter, Histogram

router = APIRouter()

# ------- Metrics latency buissness
wells_duration_seconds = Histogram(
    "wells_duration_seconds",
    "Processed time of endpoint wells",
    buckets=[0.1, 0.3, 0.5, 1, 2, 3, 5, 7.5, 10],
)
wells_total = Counter(
    "wells_total",
    "Total of requests endpoint wells",
    ["status"]
)

@router.get("/wells")
def get_wells(date_query: date, api_key: str = Depends(get_api_key)):
    """Gets list of wells.

    :param date_query: date for which the query is made.
    :return: wells
    """
    with wells_duration_seconds.time():
        try:
            id_wells = [
                {"id_well": "WELL-001"},
                {"id_well": "WELL-002"},
                {"id_well": "WELL-003"},
            ]

            wells_total.labels(status="success").inc()
            return id_wells

        except Exception:
            wells_total.labels(status="error").inc()
            raise