{{ config(materialized='table', schema='gold') }}

WITH wells AS (
    SELECT
        idpozo,
        tipopozo,
        tipoextraccion,
        tipoestado,
        formacion,
        formprod,
        tipo_de_recurso,
        sub_tipo_recurso,
        clasificacion,
        subclasificacion,
        vida_util,
        coordenadax,
        coordenaday,
        production_date,
        fecha_data,

        ROW_NUMBER() OVER (
            PARTITION BY idpozo
            ORDER BY fecha_data DESC NULLS LAST, production_date DESC NULLS LAST
        ) AS rn

    FROM {{ ref('silver_wells_production') }}
    WHERE idpozo IS NOT NULL
)

SELECT
    0 AS well_sk,
    NULL::text AS idpozo,
    'UNKNOWN'::text AS tipopozo,
    'UNKNOWN'::text AS tipoextraccion,
    'UNKNOWN'::text AS tipoestado,
    'UNKNOWN'::text AS formacion,
    'UNKNOWN'::text AS formprod,
    'UNKNOWN'::text AS tipo_de_recurso,
    'UNKNOWN'::text AS sub_tipo_recurso,
    'UNKNOWN'::text AS clasificacion,
    'UNKNOWN'::text AS subclasificacion,
    NULL::double precision AS vida_util,
    NULL::double precision AS coordenadax,
    NULL::double precision AS coordenaday

UNION ALL

SELECT
    ROW_NUMBER() OVER (ORDER BY idpozo) AS well_sk,
    idpozo,
    tipopozo,
    tipoextraccion,
    tipoestado,
    formacion,
    formprod,
    tipo_de_recurso,
    sub_tipo_recurso,
    clasificacion,
    subclasificacion,
    vida_util,
    coordenadax,
    coordenaday
FROM wells
WHERE rn = 1