"""Main module of the app FastAPI."""

from typing import Dict
from fastapi import FastAPI

from api.v1.forecast.routes import router as forecast_router
from api.v1.wells.routes import router as wells_router
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(title="Oil & Gas Forecast API")

app.include_router(forecast_router, prefix="/api/v1")
app.include_router(wells_router, prefix="/api/v1")

Instrumentator().instrument(app).expose(app)

@app.get("/hello")
def root() -> Dict[str, str]:
    """Returns Hello Message.

    :return: Hello message
    """
    return {"message": "Hello world!"}
