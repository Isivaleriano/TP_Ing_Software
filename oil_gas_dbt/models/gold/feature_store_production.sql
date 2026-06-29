{{ config(materialized='table', schema='gold') }}

with base as (

    select
        -- Fact production: se importan todas las columnas existentes del fact
        fp.*,

        -- Fecha de producción como primer día del mes, para poder hacer joins
        make_date(fp.anio, fp.mes, 1) as production_month,

        -- Dim company
        dc.idempresa,

        -- Dim date
        dd.quarter,

        -- Dim well
        dw.tipopozo,
        dw.tipoextraccion,
        dw.tipoestado,
        dw.formacion,
        dw.formprod,
        dw.tipo_de_recurso,
        dw.sub_tipo_recurso,
        dw.clasificacion,
        dw.subclasificacion,
        dw.vida_util,
        dw.coordenadax,
        dw.coordenaday,

        -- Dim location
        dl.provincia,
        dl.cuenca,
        dl.areayacimiento,
        dl.areapermisoconcesion

    from {{ ref('fact_production') }} fp

    left join {{ ref('dim_company') }} dc
        on fp.company_sk = dc.company_sk

    left join {{ ref('dim_date') }} dd
        on fp.date_sk = dd.date_sk

    left join {{ ref('dim_well') }} dw
        on fp.well_sk = dw.well_sk

    left join {{ ref('dim_location') }} dl
        on fp.location_sk = dl.location_sk

),

features as (

    select
        b.*,

        -- Petróleo: lags por mes calendario real
        pet_lag_1.prod_pet as prod_pet_lag_1,
        pet_lag_2.prod_pet as prod_pet_lag_2,
        pet_lag_3.prod_pet as prod_pet_lag_3,
        pet_lag_4.prod_pet as prod_pet_lag_4,
        pet_lag_5.prod_pet as prod_pet_lag_5,
        pet_lag_6.prod_pet as prod_pet_lag_6,
        pet_lag_12.prod_pet as prod_pet_lag_12,

        -- Gas: lags por mes calendario real
        pet_lag_1.prod_gas as prod_gas_lag_1,
        pet_lag_2.prod_gas as prod_gas_lag_2,
        pet_lag_3.prod_gas as prod_gas_lag_3,
        pet_lag_4.prod_gas as prod_gas_lag_4,
        pet_lag_5.prod_gas as prod_gas_lag_5,
        pet_lag_6.prod_gas as prod_gas_lag_6,
        pet_lag_12.prod_gas as prod_gas_lag_12,

        -- Agua: lags por mes calendario real
        pet_lag_1.prod_agua as prod_agua_lag_1,
        pet_lag_2.prod_agua as prod_agua_lag_2,
        pet_lag_3.prod_agua as prod_agua_lag_3,
        pet_lag_4.prod_agua as prod_agua_lag_4,
        pet_lag_5.prod_agua as prod_agua_lag_5,
        pet_lag_6.prod_agua as prod_agua_lag_6,
        pet_lag_12.prod_agua as prod_agua_lag_12,

        target.prod_pet as target_prod_pet_next_month

    from base b

    left join base pet_lag_1
        on b.idpozo = pet_lag_1.idpozo
       and pet_lag_1.production_month = b.production_month - interval '1 month'

    left join base pet_lag_2
        on b.idpozo = pet_lag_2.idpozo
       and pet_lag_2.production_month = b.production_month - interval '2 month'

    left join base pet_lag_3
        on b.idpozo = pet_lag_3.idpozo
       and pet_lag_3.production_month = b.production_month - interval '3 month'

    left join base pet_lag_4
        on b.idpozo = pet_lag_4.idpozo
       and pet_lag_4.production_month = b.production_month - interval '4 month'

    left join base pet_lag_5
        on b.idpozo = pet_lag_5.idpozo
       and pet_lag_5.production_month = b.production_month - interval '5 month'

    left join base pet_lag_6
        on b.idpozo = pet_lag_6.idpozo
       and pet_lag_6.production_month = b.production_month - interval '6 month'

    left join base pet_lag_12
        on b.idpozo = pet_lag_12.idpozo
       and pet_lag_12.production_month = b.production_month - interval '12 month'

    left join base target
        on b.idpozo = target.idpozo
       and target.production_month = b.production_month + interval '1 month'

)

select *
from features