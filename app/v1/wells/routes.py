"""Rutas relacionadas con operaciones de wells."""

from typing import Dict

import httpx
from fastapi import APIRouter, Depends
from app.v1.security import get_api_key
from datetime import date

router = APIRouter()


@router.get("/wells")
def get_wells(date_query: date, api_key: str = Depends(get_api_key)):
    """Obtiene listado de pozos

    :param data_query: fecha para la cual se quiere hacer la consulta
    :return: wells
    """

    id_wells = [
        {"id_well": "POZO-001"},
        {"id_well": "POZO-002"},
        {"id_well": "POZO-003"},
    ]

    return id_wells