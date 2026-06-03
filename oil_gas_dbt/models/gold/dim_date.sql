{{ config(materialized='table', schema='gold') }}

select distinct
    (anio * 100 + mes) as date_key,
    anio,
    mes,

    case
        when mes between 1 and 3 then 1
        when mes between 4 and 6 then 2
        when mes between 7 and 9 then 3
        when mes between 10 and 12 then 4
    end as quarter

from {{ ref('silver_wells_production') }}