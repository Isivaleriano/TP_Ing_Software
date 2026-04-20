"""Routes related to operations of forecast."""

from fastapi import APIRouter, Depends, HTTPException
from datetime import date
from api.v1.security import get_api_key
from prometheus_client import Counter, Histogram

router = APIRouter()

# ------- Metrics latency buissness
forecast_duration_seconds = Histogram(
    "forecast_duration_seconds",
    "Processed time of endpoint wells",
    buckets=[0.1, 0.3, 0.5, 1, 2, 3, 5, 7.5, 10],
)
forecasts_total = Counter(
    "forecasts_total",
    "Total of requests endpoint forecast",
    ["status"]
)

@router.get("/forecast")
def get_forecast(id_well: str, date_start: date, date_end: date, api_key: str = Depends(get_api_key)):
    """Gets forecast for a time horizon and a level of disaggregation.

    :param id_well: well identifier.
    :param date_start: start date of the time period.
    : param date_end: end date of the time period.
    :return: forecast
    """
    with forecast_duration_seconds.time():
        try:
            if date_end < date_start:
                raise HTTPException(status_code=400, detail="date_end must be greater than or equal to date_start")
            data = [
                {"date": date_start, "prod": 150.5},
                {"date": date_end, "prod": 160.2},
            ]
            forecasts_total.labels(status="success").inc()
            return {"id_well": id_well, "data": data}
        except Exception:
            forecasts_total.labels(status="error").inc()
            raise
