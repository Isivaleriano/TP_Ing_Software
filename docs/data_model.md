# Data Model Documentation
## Overview

The Data Warehouse is implemented in the Gold layer following a star schema design.The model is composed of one fact table and four dimensions.

## Fact Table
### fact_production
**Grain**
One row represents the production of a single well during a specific year and month.

**Measures**
- prod_pet
- prod_gas
- prod_agua
- iny_agua
- iny_gas
- iny_co2
- iny_otro
- tef
- vida_util

**Foreign Keys**
- well_key
- company_key
- location_key
- date_key

---
## Dimensions
### dim_well
Stores descriptive information about wells.
| Column | Description |
|----------|-------------|
| well_key | Surrogate key |
| idpozo | Business key |
| sigla | Well identifier |
| formprod | Production formation |
| codigopropio | Internal code |
| nombrepropio | Well name |
| coordenadax | X coordinate |
| coordenaday | Y coordinate |
| cota | Elevation |

**Business Key:** idpozo

**SCD Type:** Type 1

---
### dim_company
Stores company/operator information.
| Column | Description |
|----------|-------------|
| company_key | Surrogate key |
| idempresa | Company identifier |

**Business Key:** idempresa

**SCD Type:** Type 1

---
### dim_location
Stores geographical and operational location information.
| Column | Description |
|----------|-------------|
| location_key | Surrogate key |
| idprovincia | Province identifier |
| idcuenca | Basin identifier |
| idareapermisoconcesion | Concession area |
| idareayacimiento | Field identifier |

**SCD Type:** Type 1
---
### dim_date
Stores temporal attributes.

| Column | Description |
|----------|-------------|
| date_key | YYYYMM identifier |
| anio | Year |
| mes | Month |
| quarter | Quarter |

---
## Special Records
The dimension "dim_well" contains a record with "well_key = 0" representing unknown wells. This record is used when production records cannot be matched to a well present in the source well catalog.

---
## Entity Relationship Diagram
dim_well
    |
    |
fact_production
    |
    +---- dim_company
    |
    +---- dim_location
    |
    +---- dim_date

## Data Flow
bronze
  ↓
silver
  ↓
gold (Data Warehouse)