{{ config(materialized='table', schema='gold') }}

WITH production AS (
    SELECT
        p.idpozo,
        p.idempresa,
        p.empresa,
        p.anio,
        p.mes,
        p.production_date,

        p.provincia,
        p.cuenca,
        p.areayacimiento,

        p.prod_pet,
        p.prod_gas,
        p.prod_agua,
        p.iny_agua,
        p.iny_gas,
        p.iny_co2,
        p.iny_otro,
        p.tef
    FROM {{ ref('silver_wells_production') }} p
    WHERE p.idpozo IS NOT NULL
      AND p.anio IS NOT NULL
      AND p.mes IS NOT NULL
)

SELECT
    ROW_NUMBER() OVER (
        ORDER BY
            production.idpozo,
            production.anio,
            production.mes
    ) AS production_sk,

    COALESCE(dw.well_sk, 0) AS well_sk,
    dc.company_sk,
    dl.location_sk,
    dd.date_sk,

    production.idpozo,
    production.anio,
    production.mes,

    production.prod_pet,
    production.prod_gas,
    production.prod_agua,
    production.iny_agua,
    production.iny_gas,
    production.iny_co2,
    production.iny_otro,
    production.tef

FROM production

LEFT JOIN {{ ref('dim_well') }} dw
    ON production.idpozo = dw.idpozo

LEFT JOIN {{ ref('dim_company') }} dc
    ON production.idempresa = dc.idempresa

LEFT JOIN {{ ref('dim_location') }} dl
    ON production.provincia = dl.provincia
   AND production.cuenca = dl.cuenca
   AND production.areayacimiento = dl.areayacimiento

LEFT JOIN {{ ref('dim_date') }} dd
    ON production.anio = dd.anio
   AND production.mes = dd.mes