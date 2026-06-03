{{ config(materialized='table', schema='gold') }}

with production as (
    select
        p.idpozo,
        p.idempresa,
        (p.anio * 100 + p.mes) as date_key,

        w.idprovincia,
        w.idcuenca,
        w.idareapermisoconcesion,
        w.idareayacimiento,

        p.prod_pet,
        p.prod_gas,
        p.prod_agua,
        p.iny_agua,
        p.iny_gas,
        p.iny_co2,
        p.iny_otro,
        p.tef,
        p.vida_util
    from {{ ref('silver_wells_production') }} p
    left join {{ ref('silver_listed_wells') }} w
        on p.idpozo = w.idpozo
    where p.idpozo is not null
      and p.anio is not null
      and p.mes is not null
)

select
    row_number() over (
        order by
            production.idpozo,
            production.date_key
    ) as production_key,

    coalesce(dw.well_key, 0) as well_key,
    dc.company_key,
    dl.location_key,
    dd.date_key,

    production.prod_pet,
    production.prod_gas,
    production.prod_agua,
    production.iny_agua,
    production.iny_gas,
    production.iny_co2,
    production.iny_otro,
    production.tef,
    production.vida_util

from production

left join {{ ref('dim_well') }} dw
    on production.idpozo = dw.idpozo

left join {{ ref('dim_company') }} dc
    on production.idempresa = dc.idempresa

left join {{ ref('dim_location') }} dl
    on production.idprovincia = dl.idprovincia
   and production.idcuenca = dl.idcuenca
   and production.idareapermisoconcesion = dl.idareapermisoconcesion
   and production.idareayacimiento = dl.idareayacimiento

left join {{ ref('dim_date') }} dd
    on production.date_key = dd.date_key