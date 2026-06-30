"""Tests for forecast endpoints"""

import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from api.v1.security import get_api_key
from api.v1.main import app

route_forecast  = "/api/v1/forecast"
route_forecast_ml = "/api/v1/forecast/ml"

class TestForecast(unittest.TestCase):
    def setUp(self) -> None:
        """Starts the client test"""
        app.dependency_overrides[get_api_key] = lambda: "test-api-key"
        self.client = TestClient(app)
    
    def tearDown(self) -> None:
        """Cleans overrides to not affect other tests"""
        app.dependency_overrides = {}

    def test_hello(self) -> None:
        """Checks that ``GET /hello`` returns hello"""
        response = self.client.get("/hello")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "Hello world!"})

    def test_not_found_route(self):
        """A non-existent route must return 404"""
        response = self.client.get("/ruta-inexiste")
        self.assertEqual(response.status_code, 404)
    
    def test_status_code_ok(self):
        """GET /forecast with valid parameters must return 200"""
        response = self.client.get(
            route_forecast,
            params={
                "id_well": "WELL-001",
                "date_start": "2026-05-23",
                "date_end": "2026-05-25",
            },
        )
        self.assertEqual(response.status_code, 200)

    def test_expected_id_well(self):
        """The return contains id_well written correctly"""
        response = self.client.get(
            route_forecast,
            params={
                "id_well": "WELL-001",
                "date_start": "2026-05-23",
                "date_end": "2026-05-25",
            },
        )
        self.assertEqual(response.json()["id_well"], "WELL-001")
    
    def test_missing_id_well(self):
        """If id_well fails, it must return 422"""
        response = self.client.get(
            route_forecast,
            params={
                "date_start": "2026-05-23",
                "date_end": "2026-05-25",
            },
        )
        self.assertEqual(response.status_code, 422)
    
    def test_missing_date_start(self):
        """If date_start is missing, must return 422"""
        response = self.client.get(
            route_forecast,
            params={
                "id_well": "WELL-001",
                "date_end": "2026-05-25",
            },
        )
        self.assertEqual(response.status_code, 422)
    
    def test_missing_date_end(self):
        """If date_end is missing, must return 422"""
        response = self.client.get(
            route_forecast,
            params={
                "id_well": "WELL-001",
                "date_start": "2026-05-23",
            },
        )
        self.assertEqual(response.status_code, 422)

    def test_invalid_start_date(self):
        """If start date has incorrect format, must return 422"""
        response = self.client.get(
            route_forecast,
            params={
                "id_well": "WELL-001",
                "date_start": "invalid-date",
                "date_end": "2026-03-10",
            },
        )
        self.assertEqual(response.status_code, 422)
    
    def test_invalid_end_date(self):
        """If end date has incorrect format, must return 422"""
        response = self.client.get(
            route_forecast,
            params={
                "id_well": "WELL-001",
                "date_start": "2026-03-10",
                "date_end": "invalid-date",
            },
        )
        self.assertEqual(response.status_code, 422)
    
    def test_invalid_id_well_format(self):
        """If id_well has invalid format, must return 422"""
        response = self.client.get(
            route_forecast,
            params={
                "id_well": "POZO-001", 
                "date_start": "2026-05-23",
                "date_end": "2026-05-25",
            },
        )
        self.assertEqual(response.status_code, 422)
    
    def test_invalid_id_well_format1(self):
        """If id_well has invalid format, must return 422"""
        response = self.client.get(
            route_forecast,
            params={
                "id_well": "WELL-01", 
                "date_start": "2026-05-23",
                "date_end": "2026-05-25",
            },
        )
        self.assertEqual(response.status_code, 422)
    
    def test_invalid_id_well_format2(self):
        """If id_well has invalid format, must return 422"""
        response = self.client.get(
            route_forecast,
            params={
                "id_well": " ", 
                "date_start": "2026-05-23",
                "date_end": "2026-05-25",
            },
        )
        self.assertEqual(response.status_code, 422)
    
    def test_date_end_before_date_start(self):
        """If date_end is earlier than date_start, must return 400"""
        response = self.client.get(
            route_forecast,
            params={
                "id_well": "WELL-001",
                "date_start": "2026-05-25",
                "date_end": "2026-05-23",
            },
        )
        self.assertEqual(response.status_code, 400)

    def test_equal_start_and_end_date(self):
        """If date_start and date_end are equal, must return 200"""
        response = self.client.get(
            route_forecast,
            params={
                "id_well": "WELL-001",
                "date_start": "2026-05-23",
                "date_end": "2026-05-23",
            },
        )
        self.assertEqual(response.status_code, 200)

    def test_verb_not_allowed(self):
        """POST /forecast is not allowed, must return 405"""
        response = self.client.post(
            route_forecast,
            params={
                "id_well": "WELL-001",
                "date_start": "2026-05-23",
                "date_end": "2026-05-25",
            },
        )
        self.assertEqual(response.status_code, 405)

    def test_exact_response_structure(self):
        """Check correrct response structure"""
        response = self.client.get(
            route_forecast,
            params={
                "id_well": "WELL-001",
                "date_start": "2026-05-23",
                "date_end": "2026-05-25",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
                "id_well": "WELL-001",
                "data": [
                    {"date": "2026-05-23", "prod": 150.5},
                    {"date": "2026-05-25", "prod": 160.2},
                ],
            })
    
    def test_non_existent_well(self):
        """If well does not exist, must return 404"""
        response = self.client.get(
            route_forecast,
            params={
                "id_well": "WELL-999",
                "date_start": "2026-05-23",
                "date_end": "2026-05-25",
            },
        )
        self.assertEqual(response.status_code, 404)

    @patch("api.v1.forecast.routes.predict_one")
    def test_ml_forecast_success(self, mock_predict_one):
        """GET /forecast/ml returns prediction when model succeeds."""
        mock_predict_one.return_value = {
            "idpozo": "166925",
            "feature_anio": 2026,
            "feature_mes": 1,
            "target_anio": 2026,
            "target_mes": 2,
            "predicted_prod_pet": 6936.12,
            "model_name": "oil_production_forecaster",
            "model_version": "1",
            "model_alias": "Champion",
        }

        response = self.client.get(
            route_forecast_ml,
            params={"idpozo": "166925", "anio": 2026, "mes": 1},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["idpozo"], "166925")
        self.assertEqual(response.json()["predicted_prod_pet"], 6936.12)
        mock_predict_one.assert_called_once_with(
            idpozo="166925",
            anio=2026,
            mes=1,
        )

    @patch("api.v1.forecast.routes.predict_one")
    def test_ml_forecast_not_found(self, mock_predict_one):
        """GET /forecast/ml returns 404 when features are not found."""
        mock_predict_one.side_effect = ValueError("No features found")

        response = self.client.get(
            route_forecast_ml,
            params={"idpozo": "999999", "anio": 2026, "mes": 1},
        )

        self.assertEqual(response.status_code, 404)

    def test_ml_forecast_invalid_month(self):
        """GET /forecast/ml validates month range."""
        response = self.client.get(
            route_forecast_ml,
            params={"idpozo": "166925", "anio": 2026, "mes": 13},
        )

        self.assertEqual(response.status_code, 422)

    def test_ml_forecast_missing_idpozo(self):
        """GET /forecast/ml requires idpozo."""
        response = self.client.get(
            route_forecast_ml,
            params={"anio": 2026, "mes": 1},
        )

        self.assertEqual(response.status_code, 422)