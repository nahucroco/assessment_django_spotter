import requests


class GeocodingService:
    BASE_URL = "https://nominatim.openstreetmap.org/search"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "spotter-assessment/1.0",
            }
        )

    def geocode_station(
        self,
        name: str,
        address: str,
        city: str,
        state: str,
    ) -> dict | None:
        queries = [
            f"{name}, {city}, {state}, USA",
            f"{address}, {city}, {state}, USA",
        ]
    
        for query in queries:
            response = self.session.get(
                self.BASE_URL,
                params={
                    "q": query,
                    "format": "jsonv2",
                    "countrycodes": "us",
                    "limit": 1,
                },
                timeout=10,
            )
    
            response.raise_for_status()
    
            results = response.json()
    
            if results:
                result = results[0]
    
                return {
                    "latitude": float(result["lat"]),
                    "longitude": float(result["lon"]),
                    "source": "exact",
                }
    
        return None