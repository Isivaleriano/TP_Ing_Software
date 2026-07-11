{{ config(materialized='table', schema='gold') }}

select *
from {{ ref('feature_store_production') }}
where target_prod_pet_next_month is not null
  and target_prod_gas_next_month is not null