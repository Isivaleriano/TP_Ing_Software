"""Tests para endpoint de wells."""

import unittest
from fastapi.testclient import TestClient
from api.v1.security import get_api_key
from api.v1.main import app

route_wells  = "/api/v1/wells"

class TestWells(unittest.TestCase):
    def setUp(self) -> None:
        """Starts the client test"""
        app.dependency_overrides[get_api_key] = lambda: "test-api-key"
        self.client = TestClient(app)
    
    def tearDown(self) -> None:
        """Cleans overrides to not affect other tests"""
        app.dependency_overrides = {}

    def test_status_code_ok(self):
        """GET /wells with valid parameters must return 200"""
        response = self.client.get(
            route_wells,
            params={
                "date_query": "2026-05-23",
            },
        )
        self.assertEqual(response.status_code, 200)

    def test_response_format(self):
        """The /wells response must be a list"""
        response = self.client.get(
            route_wells,
            params={
                "date_query": "2026-05-23",
            },
        )

        body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(body, list)

    def test_id_well_is_string(self):
        """id_well for each well must be a string"""
        response = self.client.get(
            route_wells,
            params={
                "date_query": "2026-05-23",
            },
        )

        body = response.json()
        self.assertEqual(response.status_code, 200)
        for item in body:
            self.assertIsInstance(item["id_well"], str)

    def test_missing_date_query(self):
        """If date_query is missing, must return 422."""
        response = self.client.get(route_wells)
        self.assertEqual(response.status_code, 422)

    def test_invalid_date_query(self):
        """If date_query has an invalid format, must return 422"""
        response = self.client.get(
            route_wells,
            params={
                "date_query": "23-05-2026",
            },
        )
        self.assertEqual(response.status_code, 422)
    
    def test_verb_not_allowed(self):
        """POST /wells is not allowed, must return 405"""
        response = self.client.post(
            route_wells,
            params={
            "date_query": "2026-05-23",
        },
        )
        self.assertEqual(response.status_code, 405)