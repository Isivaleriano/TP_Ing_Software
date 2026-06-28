# Data Model Documentation

## Overview

The Data Warehouse follows a medallion architecture with three main layers:

- **Bronze**: raw data loaded from CSV files with technical ingestion metadata.
- **Silver**: cleaned, standardized and deduplicated operational data.
- **Gold**: dimensional model used for analytics, reporting and forecasting.

The Gold layer is implemented as a star schema composed of one fact table and four dimensions:

- `fact_production`
- `dim_well`
- `dim_company`
- `dim_location`
- `dim_date`

---
## Data Flow

```text
bronze
  ↓
silver
  ↓
gold
```
---

## Bronze Layer

The Bronze layer stores raw source data as loaded from the original CSV files. All Bronze tables include technical ingestion metadata:

| Column | Description |
|---|---|
| `load_time` | UTC timestamp indicating when the ingestion process loaded the record. |
| `source_file` | Original CSV file used during ingestion. |
| `run_id` | Unique identifier of the ingestion execution. |

### bronze.listed_wells

Raw well master data.

### bronze.wells_production

Raw monthly production data.

---
## Silver Layer

The Silver layer standardizes source fields, casts data types, trims text fields, handles missing numeric production values, and removes duplicated production records at the grain:

```text
idpozo + anio + mes
```

---
## Gold Layer

The Gold layer contains the dimensional model used for analytical consumption.

## Fact Table

### fact_production

**Grain**

One row represents the monthly production of a single well.

```text
one row per well_sk + date_sk
```

**Foreign Keys**

| Column | Description |
|---|---|
| `well_sk` | Surrogate key referencing `dim_well`. |
| `company_sk` | Surrogate key referencing `dim_company`. |
| `location_sk` | Surrogate key referencing `dim_location`. |
| `date_sk` | Surrogate key referencing `dim_date`. |

**Measures**

| Column | Description |
|---|---|
| `prod_pet` | Oil production volume. |
| `prod_gas` | Gas production volume. |
| `prod_agua` | Water production volume. |
| `iny_agua` | Water injection volume. |
| `iny_gas` | Gas injection volume. |
| `iny_co2` | CO2 injection volume. |
| `iny_otro` | Other injection volume. |
| `tef` | Effective production time or operating factor from the source dataset. |

---

## Dimensions

### dim_well

Stores descriptive information about wells.

| Column | Description |
|---|---|
| `well_sk` | Surrogate key. |
| `idpozo` | Business identifier of the well. |
| `tipopozo` | Type of well. |
| `tipoextraccion` | Extraction type. |
| `tipoestado` | Operational status of the well. |
| `formprod` | Productive formation. |
| `formacion` | Geological formation. |
| `tipo_de_recurso` | Resource type. |
| `sub_tipo_recurso` | Resource subtype. |
| `clasificacion` | Well classification. |
| `subclasificacion` | Well subclassification. |
| `vida_util` | Useful life associated with the well. |
| `coordenadax` | X coordinate. |
| `coordenaday` | Y coordinate. |

**Business Key:** `idpozo`

**SCD Type:** Type 1

**Special Record**

`dim_well` includes an unknown well record with:

```text
well_sk = 0
idpozo = 'UNKNOWN'
```

This record is used when production records cannot be matched to a known well in the well catalog.

---

### dim_company

Stores company/operator information.

| Column | Description |
|---|---|
| `company_sk` | Surrogate key. |
| `idempresa` | Business identifier of the company. |
| `empresa` | Company/operator name. |

**Business Key:** `idempresa`

**SCD Type:** Type 1

---

### dim_location

Stores geographical and operational location information.

| Column | Description |
|---|---|
| `location_sk` | Surrogate key. |
| `provincia` | Province where the well is located. |
| `cuenca` | Basin where the well is located. |
| `areayacimiento` | Field or reservoir area. |
| `areapermisoconcesion` | Permit or concession area. |

**SCD Type:** Type 1

---

### dim_date

Stores temporal attributes at monthly granularity.

| Column | Description |
|---|---|
| `date_sk` | Date surrogate key in `YYYYMM` format. |
| `anio` | Calendar year. |
| `mes` | Calendar month. |
| `quarter` | Calendar quarter. |

---

## Entity Relationship Diagram

```text
              dim_well
                 |
                 |
dim_company -- fact_production -- dim_location
                 |
                 |
              dim_date
```

---

## Notes

- The Gold model uses surrogate keys with the `_sk` suffix.
- Technical ingestion metadata is stored in Bronze only.