{{ config(materialized='table', schema='gold') }}

WITH locations AS (
    SELECT DISTINCT
        provincia,
        cuenca,
        areayacimiento,
        areapermisoconcesion
    FROM {{ ref('silver_wells_production') }}
    WHERE provincia IS NOT NULL
       OR cuenca IS NOT NULL
       OR areayacimiento IS NOT NULL
)

SELECT
    ROW_NUMBER() OVER (
        ORDER BY provincia, cuenca, areayacimiento, areapermisoconcesion
    ) AS location_sk,
    provincia,
    cuenca,
    areayacimiento,
    areapermisoconcesion
FROM locations