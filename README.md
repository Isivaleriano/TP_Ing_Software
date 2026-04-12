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

Once the server is running, the interactive documentation is available at:
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

> **Note:** The EC2 instance has a dynamic public IP that changes on restart.
> Contact the team for the current URL during the correction period.

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
```bash
http://localhost:8000/metrics
```

To verify that Prometheus is correctly scraping the API, access:
```bash
http://localhost:9090/targets
```

#### How to open the Dashboard?

1. Start all services (API + Prometheus + Grafana). It can be easily done by docker compose:
```bash
docker compose up
```

2. Open Grafana in browser:
```bash
http://localhost:3000
```

3. Login:
- User: admin
- Password: Software_tp

## Project structure

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
├── tests/
│   ├── tests_forecast.py
│   ├── tests_security.py
│   └── tests_wells.py
├── insomnia.yaml
├── openapi.yaml
└── README.md