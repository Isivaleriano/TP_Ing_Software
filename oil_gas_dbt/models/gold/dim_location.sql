{{ config(materialized='table', schema='gold') }}

select
    row_number() over (
        order by
            idprovincia,
            idcuenca,
            idareapermisoconcesion,
            idareayacimiento
    ) as location_key,

    idprovincia,
    idcuenca,
    idareapermisoconcesion,
    idareayacimiento

from (
    select distinct
        idprovincia,
        idcuenca,
        idareapermisoconcesion,
        idareayacimiento
    from {{ ref('silver_listed_wells') }}
) locations