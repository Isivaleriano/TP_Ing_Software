{{ config(materialized='table', schema='silver') }}

select distinct
    *
from bronze.listed_wells