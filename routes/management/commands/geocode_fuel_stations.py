import time

from django.core.management.base import BaseCommand

from routes.models import FuelStation
from routes.services.geocoding import GeocodingService


class Command(BaseCommand):
    help = "Geocode fuel stations and store their coordinates"

    def handle(self, *args, **options):
        service = GeocodingService()

        stations = FuelStation.objects.filter(
            latitude__isnull=True,
            longitude__isnull=True,
        )[:5]

        if not stations:
            self.stdout.write("No stations need geocoding.")
            return

        for station in stations:
            self.stdout.write(
                f"Geocoding: {station.name} - "
                f"{station.city}, {station.state}"
            )

            try:
                result = service.geocode_station(
                    name=station.name,
                    address=station.address,
                    city=station.city,
                    state=station.state,
                )

                if result:
                    station.latitude = result["latitude"]
                    station.longitude = result["longitude"]
                    station.geocoding_source = result["source"]
                    station.save(
                        update_fields=[
                            "latitude",
                            "longitude",
                            "geocoding_source",
                        ]
                    )

                    self.stdout.write(
                        self.style.SUCCESS(
                            f"  → {result['latitude']}, "
                            f"{result['longitude']} "
                            f"({result['source']})"
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING("  → No match")
                    )

            except Exception as exc:
                self.stdout.write(
                    self.style.ERROR(
                        f"  → Error: {exc}"
                    )
                )

            time.sleep(1)