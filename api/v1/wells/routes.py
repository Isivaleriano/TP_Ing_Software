"""Rutas relacionadas con operaciones de wells."""

from fastapi import APIRouter, Depends
from api.v1.security import get_api_key
from datetime import date

router = APIRouter()


@router.get("/wells")
def get_wells(date_query: date, api_key: str = Depends(get_api_key)):
    """Gets list of wells.

    :param date_query: date for which the query is made.
    :return: wells
    """

    id_wells = [
        {"id_well": "POZO-001"},
        {"id_well": "POZO-002"},
        {"id_well": "POZO-003"},
    ]

    return id_wells