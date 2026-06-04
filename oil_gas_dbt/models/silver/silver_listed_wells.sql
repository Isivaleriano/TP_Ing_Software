{{ config(materialized='table', schema='silver') }}

WITH raw AS (
    SELECT
        idpozo::text                         AS idpozo,
        TRIM(idempresa)::varchar             AS idempresa,
        TRIM(sigla)::varchar                 AS sigla,
        TRIM(formprod)::varchar              AS formprod,
        profundidad::double precision        AS profundidad,
        TRIM(areapermisoconcesion)::varchar  AS areapermisoconcesion,
        TRIM(areayacimiento)::varchar        AS areayacimiento,
        TRIM(cuenca)::varchar                AS cuenca,
        TRIM(provincia)::varchar             AS provincia,
        coordenadax::double precision        AS coordenadax,
        coordenaday::double precision        AS coordenaday,
        TRIM(clasificacion)::varchar         AS clasificacion,
        TRIM(subclasificacion)::varchar      AS subclasificacion,
        TRIM(tipo_reservorio)::varchar       AS tipo_reservorio,
        TRIM(subtipo_reservorio)::varchar    AS subtipo_reservorio,
        NULLIF(TRIM(fecha_data), '')::date   AS fecha_data,

        ROW_NUMBER() OVER (
            PARTITION BY idpozo
            ORDER BY NULLIF(TRIM(fecha_data), '')::date DESC NULLS LAST
        ) AS rn

    FROM {{ source('bronze', 'listed_wells') }}
    WHERE idpozo IS NOT NULL
)

SELECT
    idpozo,
    idempresa,
    sigla,
    formprod,
    profundidad,
    areapermisoconcesion,
    areayacimiento,
    cuenca,
    provincia,
    coordenadax,
    coordenaday,
    clasificacion,
    subclasificacion,
    tipo_reservorio,
    subtipo_reservorio,
    fecha_data
FROM raw
WHERE rn = 1