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