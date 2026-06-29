{{ config(materialized='table', schema='gold') }}

with base as (

    select
        -- Fact production: se importan todas las columnas existentes del fact
        fp.*,

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
        *,

        -- Lags petróleo: producción de petróleo de meses anteriores
        lag(prod_pet, 1) over (
            partition by idpozo
            order by anio, mes
        ) as prod_pet_lag_1,

        lag(prod_pet, 2) over (
            partition by idpozo
            order by anio, mes
        ) as prod_pet_lag_2,

        lag(prod_pet, 3) over (
            partition by idpozo
            order by anio, mes
        ) as prod_pet_lag_3,

        lag(prod_pet, 4) over (
            partition by idpozo
            order by anio, mes
        ) as prod_pet_lag_4,

        lag(prod_pet, 5) over (
            partition by idpozo
            order by anio, mes
        ) as prod_pet_lag_5,

        lag(prod_pet, 6) over (
            partition by idpozo
            order by anio, mes
        ) as prod_pet_lag_6,

        lag(prod_pet, 12) over (
            partition by idpozo
            order by anio, mes
        ) as prod_pet_lag_12,

        -- Lags gas: producción de gas de meses anteriores
        lag(prod_gas, 1) over (
            partition by idpozo
            order by anio, mes
        ) as prod_gas_lag_1,

        lag(prod_gas, 2) over (
            partition by idpozo
            order by anio, mes
        ) as prod_gas_lag_2,

        lag(prod_gas, 3) over (
            partition by idpozo
            order by anio, mes
        ) as prod_gas_lag_3,

        lag(prod_gas, 4) over (
            partition by idpozo
            order by anio, mes
        ) as prod_gas_lag_4,

        lag(prod_gas, 5) over (
            partition by idpozo
            order by anio, mes
        ) as prod_gas_lag_5,

        lag(prod_gas, 6) over (
            partition by idpozo
            order by anio, mes
        ) as prod_gas_lag_6,

        lag(prod_gas, 12) over (
            partition by idpozo
            order by anio, mes
        ) as prod_gas_lag_12,

        -- Lags agua: producción de agua de meses anteriores
        lag(prod_agua, 1) over (
            partition by idpozo
            order by anio, mes
        ) as prod_agua_lag_1,

        lag(prod_agua, 2) over (
            partition by idpozo
            order by anio, mes
        ) as prod_agua_lag_2,

        lag(prod_agua, 3) over (
            partition by idpozo
            order by anio, mes
        ) as prod_agua_lag_3,

        lag(prod_agua, 4) over (
            partition by idpozo
            order by anio, mes
        ) as prod_agua_lag_4,

        lag(prod_agua, 5) over (
            partition by idpozo
            order by anio, mes
        ) as prod_agua_lag_5,

        lag(prod_agua, 6) over (
            partition by idpozo
            order by anio, mes
        ) as prod_agua_lag_6,

        lag(prod_agua, 12) over (
            partition by idpozo
            order by anio, mes
        ) as prod_agua_lag_12,

        -- Target: lo que queremos predecir
        lead(prod_pet, 1) over (
            partition by idpozo
            order by anio, mes
        ) as target_prod_pet_next_month

    from base

)

select *
from features
where target_prod_pet_next_month is not null
  and prod_pet_lag_1 is not null
  and prod_pet_lag_2 is not null
  and prod_pet_lag_3 is not null
  and prod_pet_lag_4 is not null
  and prod_pet_lag_5 is not null
  and prod_pet_lag_6 is not null
  and prod_pet_lag_12 is not null