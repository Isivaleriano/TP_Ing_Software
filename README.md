# Oil & Gas Forecast API

REST API mock built with FastAPI for forecasting hydrocarbon production.
Developed as part of the Software Engineering course.

## Team

- Isidro Valeriano
- Florencia Zoffi
- María Belén Depalo

## Description

This project is a mock REST API that simulates a hydrocarbon production 
forecasting platform. It exposes endpoints to query wells and their 
production forecasts, secured via API Key authentication. It also includes
a full data integration pipeline with Bronze, Silver and Gold layers,
orchestrated by Apache Airflow and visualized through Metabase.

## Requirements

- Docker
- Python 3.10+

## How to run locally

**1. Clone the repository:**
```bash
git clone https://github.com/Isivaleriano/TP_Ing_Software.git
cd TP_Ing_Software
```

**2. Install dependencies:**
```bash
pip install -r api/v1/requirements.txt
```

**3. Run the server:**
```bash
uvicorn api.v1.main:app --host 0.0.0.0 --port 8000
```

**4. Or run all services with Docker Compose:**
```bash
docker compose up -d
```

## Live Demo

All services are publicly available:

| Service | URL | Credentials |
|---------|-----|-------------|
| Swagger UI | http://100.58.114.58:8000/docs | X-API-Key: abcdef12345 |
| OpenAPI JSON | http://100.58.114.58:8000/openapi.json | - |
| Metrics | http://100.58.114.58:8000/metrics | - |
| Prometheus | http://100.58.114.58:9090 | - |
| Grafana | http://100.58.114.58:3001 | admin / Software_tp |
| Airflow | http://100.58.114.58:8090 | admin / admin |
| Metabase | http://100.58.114.58:3000 | - |

> **Note:** The EC2 instance has a dynamic public IP that changes on restart.
> Contact the team for the current URL during the correction period.

## API Documentation

All endpoints require the header `X-API-Key: abcdef12345`.

### Forecast API

The project exposes two forecasting endpoints:

- **`/api/v1/forecast`** — original mock endpoint developed during Phases 1 and 2. It is kept for backward compatibility and demonstration purposes.
- **`/api/v1/forecast/ml`** — machine learning inference endpoint introduced in Phase 3. This endpoint loads the Champion model from the MLflow Model Registry and retrieves the required features from the Gold Feature Store before generating the prediction.

### GET /api/v1/wells

Returns the list of available wells for a given date.

**Query parameters:**
| Parameter  |       Type        | Required |     Description    |
|------------|-------------------|----------|--------------------|
| date_query | date (YYYY-MM-DD) |   Yes    | Date for the query |

**Example request:**
```bash
curl -X GET "http://localhost:8000/api/v1/wells?date_query=2023-10-01" \
     -H "X-API-Key: abcdef12345"
```

**Example response:**
```json
[
  {"id_well": "POZO-001"},
  {"id_well": "POZO-002"},
  {"id_well": "POZO-003"}
]
```

### GET /api/v1/forecast

Returns the production forecast for a given well and time horizon.

**Query parameters:**
| Parameter  |        Type       | Required |   Description   |
|------------|-------------------|----------|-----------------|
|   id_well  |       string      |    Yes   | Well identifier |
| date_start | date (YYYY-MM-DD) |    Yes   |    Start date   |
|  date_end  | date (YYYY-MM-DD) |    Yes   |     End date    |

**Example request:**
```bash
curl -X GET "http://localhost:8000/api/v1/forecast?id_well=POZO-001&date_start=2023-10-01&date_end=2023-10-10" \
     -H "X-API-Key: abcdef12345"
```

**Example response:**
```json
{
  "id_well": "POZO-001",
  "data": [
    {"date": "2023-10-01", "prod": 150.5},
    {"date": "2023-10-10", "prod": 160.2}
  ]
}
```

## Authentication

All endpoints are protected by an API Key sent via HTTP header:

X-API-Key: abcdef12345

Requests without a valid key return HTTP 403 Forbidden.

## Deployment

The API is deployed on AWS EC2 (t3.xlarge) using Docker Compose. The deployment
is automated via GitHub Actions — every push to `main` that passes tests
automatically builds, publishes and deploys the new image to the EC2 instance.

## CI/CD

Two GitHub Actions workflows are configured:

- **tests.yml** — runs on every push and pull request. Executes unit tests and linter.
- **docker_publish.yml** — runs on push to `main`. Builds and publishes the Docker image to GitHub Container Registry, then deploys automatically to EC2.

## Running tests

```bash
python -m unittest discover -s tests
```

## Monitoring Dashboard

A monitoring dashboard is implemented using **Prometheus** and **Grafana**.

- **FastAPI** exposes metrics via `/metrics`
- **Prometheus** scrapes metrics every 15 seconds
- **Grafana** visualizes data and manages alerting

Access Grafana at `http://100.58.114.58:3001` (admin / Software_tp).

An alerting system detects service outages, high error rates and performance degradation.

## Data Integration

### Architecture

The project follows a Medallion Architecture with three layers:

**Bronze** — raw data ingested from Argentina's public oil and gas datasets (datos.gob.ar).

**Silver** — cleaned and standardized data:
- `silver_listed_wells`
- `silver_wells_production`

**Gold** — star schema optimized for analytics:
- `dim_company`, `dim_date`, `dim_location`, `dim_well`
- `fact_production` (grain: one row per well per month)

### Orchestration

The data pipeline is orchestrated by **Apache Airflow** running on port 8090.
The DAG `oil_gas_pipeline` runs daily at 06:00 UTC with the following tasks:

1. `extract_data` — downloads raw CSVs from official sources
2. `load_bronze` — loads CSVs into PostgreSQL bronze schema
3. `dbt_run` — builds Silver and Gold layers
4. `dbt_test` — runs data quality checks
5. `persist_quality_results` — persists test results to PostgreSQL

To update the workflows, trigger a new DAG run from the Airflow UI at
`http://100.58.114.58:8090` or push a change to `main`.

### BI Platform

**Metabase** is available at `http://100.58.114.58:3000`. It connects directly
to the PostgreSQL data warehouse and exposes Bronze, Silver, Gold and Public
schemas for exploration by non-technical users.

### Data Quality

Data quality checks are implemented using dbt tests covering:

- Completeness (`not_null`)
- Uniqueness (`unique`)
- Validity (`accepted_values`)
- Referential integrity (`relationships`)
- Business rules (`expression_is_true`)

Results are persisted in the `quality.test_results` table in PostgreSQL and
are visible in Metabase under the quality schema.

### Feature Store

Two Gold dbt models support the production forecasting model (Phase 3):

- `gold.feature_store_production` — every well-month, with lag features
  (`prod_pet_lag_1`...`lag_12`, and the same for gas/water) computed by calendar
  month rather than row position, so wells with gaps in their reporting history
  don't get a mislabeled lag. Includes each well's most recent month, used for
  inference.
- `gold.training_dataset_production` — the same table filtered to rows with a
  known `target_prod_pet_next_month`, used for training.

### Data Governance

Data governance is implemented through dbt documentation and a DataHub catalog
(search, ownership, docs, and lineage across Bronze, Silver and Gold).

DataHub is **not part of the public live demo** above — it does not run on the EC2 instance. It runs on demand via Docker Compose, on whichever machine needs to browse it:

```bash
docker compose -f datahub/docker-compose.yml up -d
cd oil_gas_dbt && dbt docs generate && cd ..
./datahub/ingest.sh
```

Once running, the catalog and lineage graph are browsable at `http://localhost:9002`
(login `datahub` / `datahub`). See [datahub/README.md](datahub/README.md) for details.

### Running the pipeline manually

```bash
python src/ingestion/extract_data.py
dbt run
dbt test
```

## Project structure

```bash
TP_Ing_Software/
├── .github/
│   └── workflows/
│       ├── docker_publish.yml
│       └── tests.yml
├── api/
│   └── v1/
│       ├── forecast/
│       │   └── routes.py
│       ├── wells/
│       │   └── routes.py
│       ├── Dockerfile
│       ├── main.py
│       ├── requirements.txt
│       └── security.py
├── dags/
│   └── oil_gas_pipeline.py
├── datahub/
│   ├── docker-compose.yml
│   ├── recipe_postgres.yml
│   ├── recipe_dbt.yml
│   └── ingest.sh
├── monitoring/
│   ├── grafana/
│   └── prometheus/
├── oil_gas_dbt/
│   └── models/
│       ├── silver/
│       └── gold/
├── src/
│   ├── ingestion/
│   │   └── extract_data.py
│   ├── transformations/
│   ├── warehouse/
│   │   └── load_bronze.py
│   └── quality/
│       └── persist_dbt_results.py
├── tests/
│   ├── tests_forecast.py
│   ├── tests_security.py
│   └── tests_wells.py
├── adrs/
├── docker-compose.yml
├── Dockerfile.airflow
├── insomnia.yaml
├── openapi.yaml
└── README.md
```