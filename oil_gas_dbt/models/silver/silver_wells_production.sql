{{ config(materialized='table', schema='silver') }}

WITH raw AS (
    SELECT
        idpozo::text                         AS idpozo,
        TRIM(idempresa)::varchar             AS idempresa,
        TRIM(empresa)::varchar               AS empresa,
        anio::int                            AS anio,
        mes::int                             AS mes,

        COALESCE(prod_pet, 0)::double precision   AS prod_pet,
        COALESCE(prod_gas, 0)::double precision   AS prod_gas,
        COALESCE(prod_agua, 0)::double precision  AS prod_agua,
        COALESCE(iny_agua, 0)::double precision   AS iny_agua,
        COALESCE(iny_gas, 0)::double precision    AS iny_gas,
        COALESCE(iny_co2, 0)::double precision    AS iny_co2,
        COALESCE(iny_otro, 0)::double precision   AS iny_otro,
        COALESCE(tef, 0)::double precision        AS tef,

        TRIM(tipoextraccion)::varchar        AS tipoextraccion,
        TRIM(tipoestado)::varchar            AS tipoestado,
        TRIM(tipopozo)::varchar              AS tipopozo,
        TRIM(provincia)::varchar             AS provincia,
        TRIM(cuenca)::varchar                AS cuenca,
        TRIM(areayacimiento)::varchar        AS areayacimiento,
        TRIM(tipo_de_recurso)::varchar       AS tipo_de_recurso,

        NULLIF(TRIM(fecha_data), '')::date   AS fecha_data,
        MAKE_DATE(anio::int, mes::int, 1)    AS production_date,

        ROW_NUMBER() OVER (
            PARTITION BY idpozo, anio, mes
            ORDER BY NULLIF(TRIM(fecha_data), '')::date DESC NULLS LAST
        ) AS rn

    FROM {{ source('bronze', 'wells_production') }}
    WHERE idpozo IS NOT NULL
      AND anio IS NOT NULL
      AND mes IS NOT NULL
      AND mes BETWEEN 1 AND 12
)

SELECT
    idpozo,
    idempresa,
    empresa,
    anio,
    mes,
    prod_pet,
    prod_gas,
    prod_agua,
    iny_agua,
    iny_gas,
    iny_co2,
    iny_otro,
    tef,
    tipoextraccion,
    tipoestado,
    tipopozo,
    provincia,
    cuenca,
    areayacimiento,
    tipo_de_recurso,
    fecha_data,
    production_date
FROM raw
WHERE rn = 1