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
production forecasts, secured via API Key authentication.

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

**4. Or run with Docker:**
```bash
docker pull ghcr.io/isivaleriano/tp_ing_software:latest
docker run -d --name forecast-api -p 8000:8000 ghcr.io/isivaleriano/tp_ing_software:latest
```

## API Documentation

### Production Environment (AWS EC2)

Interactive Swagger documentation:

http://52.87.250.147:8000/docs

OpenAPI specification:

http://52.87.250.147:8000/openapi.json

### Local Environment

http://localhost:8000/docs

## Endpoints

All endpoints require the header `X-API-Key: abcdef12345`.

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

The API is deployed on AWS EC2 using Docker. The deployment is automated 
via GitHub Actions — every push to `main` that passes tests automatically 
builds, publishes and deploys the new image to the EC2 instance.

### Production URLs

- API Documentation: http://52.87.250.147:8000/docs
- OpenAPI Specification: http://52.87.250.147:8000/openapi.json
- Prometheus: http://52.87.250.147:9090
- Grafana: http://52.87.250.147:3001

Grafana credentials:

- User: admin
- Password: Software_tp

> Note: The application is deployed on an AWS EC2 instance through an automated CI/CD pipeline using GitHub Actions.

## CI/CD

Two GitHub Actions workflows are configured:

- **tests.yml** — runs on every push and pull request. Executes unit tests and linter.
- **docker_publish.yml** — runs on push to `main`. Builds and publishes the Docker image to GitHub Container Registry, then deploys automatically to EC2.

## Running tests
Functional tests of endpoints and security tests were implemented to validate API Key authentication across all endpoints.
To run all tests:
```bash
python -m unittest discover -s tests
```
To run a specific test file:
```bash
python -m unittest discover -s tests/tests_forecast.py
```
To run a specific test:
```bash
python -m unittest discover -s tests/tests_forecast.py/test_status_code_ok
```

## Dashboard

A monitoring dashboard was implemented using **Prometheus** and **Grafana** to ensure system performance, reliability and observability.

### Monitoring Architecture

- **FastAPI** exposes metrics via `/metrics` using `prometheus-fastapi-instrumentator`
- **Prometheus** scrapes metrics from the API
- **Grafana** visualizes the data and manages alerting

The system is orchestrated using Docker. 

## System Performance Metrics

The API exposes metrics at:

Production:
http://52.87.250.147:8000/metrics

Local:
http://localhost:8000/metrics

To verify that Prometheus is correctly scraping the API, access:
```bash
http://localhost:9090/targets
```

#### How to open the Dashboard?

1. Start all services (API + Prometheus + Grafana). It can be easily done by docker compose:
```bash
docker compose up --build
```

2. Open Grafana in browser

Production:
http://52.87.250.147:3001

Local:
http://localhost:3001

3. Login:
- User: admin
- Password: Software_tp

### Alerts
An alerting system is in place to detect abnormal system behavior, including service outages, high error rates, and performance degradation.
Note: Email notifications are not fully configured due to AWS cost constraints. The system is prepared to support notification channels if needed.

#### Dashboard Notes
- Metrics are updated in near real-time
- Some panels require continuous traffic to display values
- To test alerting behavior, manual requests or simulated failures can be performed

## Live Demo

The application is publicly available for evaluation:

| Service | URL |
|----------|----------|
| Swagger UI | http://52.87.250.147:8000/docs |
| OpenAPI JSON | http://52.87.250.147:8000/openapi.json |
| Forecast API | http://52.87.250.147:8000/api/v1 |
| Metrics | http://52.87.250.147:8000/metrics |
| Prometheus | http://52.87.250.147:9090 |
| Grafana | http://52.87.250.147:3001 |

Grafana credentials:

- User: admin
- Password: Software_tp




# Data Integration
## Data Engineering Architecture

The project follows a Medallion Architecture composed of three layers.

### Bronze Layer

Stores raw data ingested from Argentina's public oil and gas datasets (`datos.gob.ar`). Data in this layer is preserved without modifications to ensure reproducibility and future reprocessing.

### Silver Layer

Contains cleaned and standardized data. Transformations include:

- Type casting
- Null handling
- Deduplication
- String trimming
- Domain validation

Silver models:

- `silver_listed_wells`
- `silver_wells_production`

### Gold Layer

Implements a dimensional model optimized for analytics using a star schema.

Dimensions:

- `dim_company`
- `dim_date`
- `dim_location`
- `dim_well`

Fact table:

- `fact_production`

The grain of the fact table is:

> One row per well (`idpozo`) per month (`anio`, `mes`).

---

## Data Warehouse Setup

### PostgreSQL Schemas

The warehouse is organized into three schemas:

```text
bronze
silver
gold
```

---

## Running the Data Pipeline

### 1. Load raw data into Bronze

Run the ingestion scripts:

```bash
python src/ingestion/extract_data.py
```

### 2. Execute dbt transformations

Run all models:

```bash
dbt run
```

Run a specific layer:

```bash
dbt run --select silver
dbt run --select gold
```

### 3. Execute data quality tests

Run all tests:

```bash
dbt test
```

Run tests for a specific model:

```bash
dbt test --select silver_wells_production
```

---

## Data Quality

The project implements automated data quality checks using dbt.

Implemented dimensions of quality include:

* Completeness (`not_null`)
* Uniqueness (`unique`)
* Validity (`accepted_values`)
* Referential integrity (`relationships`)
* Business rules (`expression_is_true`)

Some tests are configured as **warnings** instead of **errors** when source system inconsistencies are known and should not block the pipeline.

Example:

* Production wells that do not exist in `listed_wells` are flagged as warnings because removing them would result in data loss.

---

## Data Governance

Data governance is implemented through:

* dbt documentation
* DataHub metadata catalog
* Ownership metadata
* Table lineage
* Last update tracking

Metadata includes:

* Data owners
* Teams
* Sensitivity levels
* PII indicators


### Generating Documentation

Generate dbt documentation:

```bash
dbt docs generate
```


### DataHub

Generate metadata and lineage:

```bash
datahub ./ingest.sh
```

Open DataHub:

```text
http://localhost:9002
```

Features:

* Table exploration
* Column documentation
* Ownership
* Lineage visualization
* Last synchronization information

---

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
├── monitoring/
│   ├── grafana/
│   │   ├── dasboards/
│   │   │   └── monitoring.json
│   │   └── provisioning
│   │       ├── alerting
│   │       │   ├── contactpoint.yml
│   │       │   └── notificationpolicies.yml               
│   │       ├── dashboards
│   │       │   └── dashboard.yml
│   │       └── datasources
│   │           └── prometheus.yml
│   └── prometheus/
│       ├──rules/
│       │   └── alerts.yml
│       └── prometheus.yml
├── tests/
│   ├── tests_forecast.py
│   ├── tests_security.py
│   └── tests_wells.py
├── docker-compose.yml
├── insomnia.yaml
├── openapi.yaml
└── README.md