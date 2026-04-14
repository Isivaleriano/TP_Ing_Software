"""Routes related to operations of forecast."""

from fastapi import APIRouter, Depends
from datetime import date
from api.v1.security import get_api_key
from prometheus_client import Histogram

router = APIRouter()


"""Routes related to operations of forecast."""

from datetime import date

from fastapi import APIRouter, Depends
from prometheus_client import Histogram

from api.v1.security import get_api_key

router = APIRouter()

# ------- Métrica custom para medir únicamente la latencia del endpoint forecast -----
forecast_duration_seconds = Histogram(
    "forecast_duration_seconds",
    "Tiempo de procesamiento del endpoint forecast",
    buckets=[0.1, 0.3, 0.5, 1, 2, 3, 5, 7.5, 10],
)

@router.get("/forecast")
def get_forecast(id_well: str, date_start: date, date_end: date, api_key: str = Depends(get_api_key)):
    """Gets baseline forecast for a given time and level of disaggregation.

    :param id_well: well identifier.
    :param date_start: Start date well.
    :param date_end: End date well.
    :return: id_well, data.
    """
    with forecast_duration_seconds.time():
        data = [
            {"date": date_start, "prod": 150.5},
            {"date": date_end, "prod": 160.2},
        ]

        return {"id_well": id_well, "data": data}