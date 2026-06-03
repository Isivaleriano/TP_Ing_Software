{{ config(materialized='table', schema='gold') }}

select
    0 as well_key,
    null::bigint as idpozo,
    'UNKNOWN' as sigla,
    null::text as formprod,
    null::text as codigopropio,
    null::text as nombrepropio,
    null::double precision as coordenadax,
    null::double precision as coordenaday,
    null::double precision as cota

union all

select
    row_number() over (order by idpozo) as well_key,
    idpozo,
    sigla,
    formprod,
    codigopropio,
    nombrepropio,
    coordenadax,
    coordenaday,
    cota
from (
    select distinct
        idpozo,
        sigla,
        formprod,
        codigopropio,
        nombrepropio,
        coordenadax,
        coordenaday,
        cota
    from {{ ref('silver_listed_wells') }}
    where idpozo is not null
) wells