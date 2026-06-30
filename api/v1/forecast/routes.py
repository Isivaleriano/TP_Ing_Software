"""Routes related to operations of forecast."""

from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import date
from api.v1.security import get_api_key
from prometheus_client import Counter, Histogram
from typing import Annotated

from ml.predict import predict_one  
from pydantic import BaseModel

router = APIRouter()

class ForecastMLResponse(BaseModel):
    idpozo: str
    feature_anio: int
    feature_mes: int
    target_anio: int
    target_mes: int
    predicted_prod_pet: float
    model_name: str
    model_version: str
    model_alias: str


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

VALID_WELLS = ["WELL-001", "WELL-002", "WELL-003"]

@router.get("/forecast")
def get_forecast(id_well: Annotated[str, Query(pattern=r"^WELL-\d{3}$")], 
                 date_start: date, 
                 date_end: date, 
                 api_key: str = Depends(get_api_key)):
    """Gets forecast for a time horizon and a level of disaggregation.

    :param id_well: well identifier.
    :param date_start: start date of the time period.
    : param date_end: end date of the time period.
    :return: forecast
    """
    with forecast_duration_seconds.time():
        try:
            if date_end < date_start:
                raise HTTPException( status_code=400, detail="date_end must be greater than or equal to date_start")
            if id_well not in VALID_WELLS:
                raise HTTPException( status_code=404, detail=f"Well {id_well} not found" )
            data = [
                {"date": date_start, "prod": 150.5},
                {"date": date_end, "prod": 160.2},
            ]
            forecasts_total.labels(status="success").inc()
            return {"id_well": id_well, "data": data}
        except Exception:
            forecasts_total.labels(status="error").inc()
            raise

@router.get("/forecast/ml", response_model=ForecastMLResponse)
def get_ml_forecast(
    idpozo: str = Query(..., description="Identificador real del pozo en Gold"),
    anio: int = Query(..., ge=1900, le=2100),
    mes: int = Query(..., ge=1, le=12),
    api_key: str = Depends(get_api_key),
):
    """
    Generates a production forecast using the registered ML model.

    :param idpozo: Well identifier.
    :param anio: Feature year.
    :param mes: Feature month.
    :return: Predicted oil production for the following month.
    """
    with forecast_duration_seconds.time():
        try:
            result = predict_one(idpozo=idpozo, anio=anio, mes=mes)

            forecasts_total.labels(status="success").inc()
            return result

        except ValueError as e:
            forecasts_total.labels(status="error").inc()
            raise HTTPException(status_code=404, detail=str(e))

        except Exception as e:
            forecasts_total.labels(status="error").inc()
            raise HTTPException(
                status_code=500,
                detail="Internal error while generating ML forecast",
            )