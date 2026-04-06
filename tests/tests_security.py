"""Tests para revisar seguridad."""

import unittest
from fastapi.testclient import TestClient
from fastapi import HTTPException
from api.v1.security import get_api_key
from api.v1.main import app

route_forecast  = "/api/v1/forecast"
route_wells  = "/api/v1/wells"

class TestSecurity(unittest.TestCase):
    def setUp(self) -> None:
        """Starts the client test"""
        self.client = TestClient(app)
    
    def test_valid_key(self):
        """get_api_key must return the key if valid"""
        result = get_api_key("abcdef12345")
        self.assertEqual(result, "abcdef12345")
    
    def test_invalid_key(self):
        """get_api_key must throw HTTPException 403 if invalid key"""
        with self.assertRaises(HTTPException) as context:
            get_api_key("clave-incorrecta")
        self.assertEqual(context.exception.status_code, 403)
        self.assertEqual(
            context.exception.detail,
            "Acceso denegado. API Key inválida o faltante en el header."
        )

    def test_none_key(self):
        """get_api_key must throw HTTPException 403 if no key is sent"""
        with self.assertRaises(HTTPException) as context:
            get_api_key(None)

        self.assertEqual(context.exception.status_code, 403)
        self.assertEqual(
            context.exception.detail,
            "Acceso denegado. API Key inválida o faltante en el header."
        )

    def test_forecast_valid_api_key(self):
        """Forecast with invalid API must return 200"""
        response = self.client.get(
            route_forecast,
            params={
                "id_well": "POZO-001",
                "date_start": "2026-05-23",
                "date_end": "2026-05-25",
            },
            headers={
                "X-API-Key": "abcdef12345",
            },
        )
        self.assertEqual(response.status_code, 200)

    def test_forecast_without_api_key_(self):
        """Forecast without API key must return 403"""
        response = self.client.get(
            route_forecast,
            params={
                "id_well": "POZO-001",
                "date_start": "2026-05-23",
                "date_end": "2026-05-25",
            },
        )
        self.assertEqual(response.status_code, 403)

    def test_forecast_with_invalid_api_key(self):
        """Forecast with invalid API key must return 403"""
        response = self.client.get(
            route_forecast,
            params={
                "id_well": "POZO-001",
                "date_start": "2026-05-23",
                "date_end": "2026-05-25",
            },
            headers={
                "X-API-Key": "clave-incorrecta",
            },
        )
        self.assertEqual(response.status_code, 403)

    def test_forecast_security_error_message(self):
        """Forecast without API key musrt return the correct error message"""
        response = self.client.get(
            route_forecast,
            params={
                "id_well": "POZO-001",
                "date_start": "2026-05-23",
                "date_end": "2026-05-25",
            },
        )
        body = response.json()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            body["detail"],
            "Acceso denegado. API Key inválida o faltante en el header."
        )

    def test_wells_with_valid_api_key(self):
        """Wells with valid API key must return 200"""
        response = self.client.get(
            route_wells,
            params={
                "date_query": "2026-05-23",
            },
            headers={
                "X-API-Key": "abcdef12345",
            },
        )
        self.assertEqual(response.status_code, 200)
    
    def test_wells_without_api_key(self):
        """Wells without API key must return 403"""
        response = self.client.get(
            route_wells,
            params={
                "date_query": "2026-05-23",
            },
        )
        self.assertEqual(response.status_code, 403)
    
    def test_wells_with_invalid_api_key(self):
        """Wells with invalid API key must return 403"""
        response = self.client.get(
            route_wells,
            params={
                "date_query": "2026-05-23",
            },
            headers={
                "X-API-Key": "clave-incorrecta",
            },
        )
        self.assertEqual(response.status_code, 403)
    
    def test_wells_security_error_message(self):
        """Wells without API key must return correct error messaged"""
        response = self.client.get(
            route_wells,
            params={
                "date_query": "2026-05-23",
            },
        )
        body = response.json()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            body["detail"],
            "Acceso denegado. API Key inválida o faltante en el header."
        )