import requests
from django.conf import settings


class RoutingService:
    BASE_URL = "https://api.heigit.org/openrouteservice/v2/directions/driving-car"

    def get_route(self, start: tuple[float, float], finish: tuple[float, float]) -> dict:
        body = {
            "coordinates": [
                list(start),
                list(finish),
            ],
            "instructions": False,
        }

        headers = {
            "Authorization": settings.OPENROUTESERVICE_API_KEY,
            "Content-Type": "application/json",
        }

        response = requests.post(
            self.BASE_URL,
            json=body,
            headers=headers,
            timeout=10,
        )

        response.raise_for_status()

        return response.json()