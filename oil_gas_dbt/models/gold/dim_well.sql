{{ config(materialized='table', schema='gold') }}

SELECT
    0 AS well_sk,
    NULL::text AS idpozo,
    'UNKNOWN'::text AS sigla,
    NULL::text AS formprod,
    NULL::double precision AS profundidad,
    NULL::double precision AS coordenadax,
    NULL::double precision AS coordenaday,
    NULL::text AS clasificacion,
    NULL::text AS subclasificacion,
    NULL::text AS tipo_reservorio,
    NULL::text AS subtipo_reservorio

UNION ALL

SELECT
    ROW_NUMBER() OVER (ORDER BY idpozo) AS well_sk,
    idpozo,
    sigla,
    formprod,
    profundidad,
    coordenadax,
    coordenaday,
    clasificacion,
    subclasificacion,
    tipo_reservorio,
    subtipo_reservorio
FROM (
    SELECT DISTINCT
        idpozo,
        sigla,
        formprod,
        profundidad,
        coordenadax,
        coordenaday,
        clasificacion,
        subclasificacion,
        tipo_reservorio,
        subtipo_reservorio
    FROM {{ ref('silver_listed_wells') }}
    WHERE idpozo IS NOT NULL
) wells