"""Main module of the app FastAPI."""

from typing import Dict
from fastapi import FastAPI

from app.v1.forecast.routes import router as forecast_router
from app.v1.wells.routes import router as wells_router

app = FastAPI(title="Oil & Gas Forecast API")

app.include_router(forecast_router, prefix="/api/v1")
app.include_router(wells_router, prefix="/api/v1")

@app.get("/hello")
def root() -> Dict[str, str]:
    """Devuelve un saludo.

    :return: Mensaje de saludo.
    """
    return {"message": "Hola mundo!"}
