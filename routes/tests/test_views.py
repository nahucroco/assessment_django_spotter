from unittest.mock import patch

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient


class RoutePlanningViewTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.url = "/api/routes/"

    def test_valid_request_returns_200(self):
        response = self.client.post(
            self.url,
            {
                "start": {
                    "latitude": 40.7128,
                    "longitude": -74.0060,
                },
                "finish": {
                    "latitude": 41.8781,
                    "longitude": -87.6298,
                },
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn("route", response.data)
        self.assertIn("fuel", response.data)

        self.assertIn("distance_miles", response.data["route"])
        self.assertIn("geometry", response.data["route"])

        self.assertIn("total_cost", response.data["fuel"])
        self.assertIn("stops", response.data["fuel"])

    def test_invalid_coordinates_return_400(self):
        response = self.client.post(
            self.url,
            {
                "start": {
                    "latitude": 200,
                    "longitude": -74.0060,
                },
                "finish": {
                    "latitude": 41.8781,
                    "longitude": -87.6298,
                },
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    @patch("routes.views.RoutePlanningService.plan_route")
    def test_routing_error_returns_502(self, mock_plan_route):
        from requests import RequestException

        mock_plan_route.side_effect = RequestException()

        response = self.client.post(
            self.url,
            {
                "start": {
                    "latitude": 40.7128,
                    "longitude": -74.0060,
                },
                "finish": {
                    "latitude": 41.8781,
                    "longitude": -87.6298,
                },
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_502_BAD_GATEWAY,
        )

    @patch("routes.views.RoutePlanningService.plan_route")
    def test_unreachable_route_returns_422(self, mock_plan_route):
        mock_plan_route.side_effect = ValueError("Cannot reach next fuel station.")

        response = self.client.post(
            self.url,
            {
                "start": {
                    "latitude": 40.7128,
                    "longitude": -74.0060,
                },
                "finish": {
                    "latitude": 41.8781,
                    "longitude": -87.6298,
                },
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
