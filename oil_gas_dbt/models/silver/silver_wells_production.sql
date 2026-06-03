{{ config(materialized='table', schema='silver') }}

select distinct
    *
from bronze.wells_production