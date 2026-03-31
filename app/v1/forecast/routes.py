"""Routes related to operations of forecast."""

from typing import Dict

import httpx
from fastapi import APIRouter, Depends
from datetime import date
from app.v1.security import get_api_key

router = APIRouter()


@router.get("/forecast")
def get_forecast(id_well: str, date_start: date, date_end: date, api_key: str = Depends(get_api_key)):
    """Obtiene pronónstico base para un horizonte de tiempo y nivel de desagregación.

    :param id_well: Identificador del pozo.
    :param date_start: Inicia el pozo.
    :return: id_well, data.
    """
    data = [
        {"date": date_start, "prod": 150.5},
        {"date": date_end, "prod": 160.2},
    ]

    return {"id_well": id_well, "data": data}