{{ config(materialized='table', schema='gold') }}

select
    row_number() over (order by idempresa) as company_sk,
    idempresa
from (
    select distinct
        idempresa
    from {{ ref('silver_listed_wells') }}
    where idempresa is not null
) companies