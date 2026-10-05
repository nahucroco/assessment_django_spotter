from django.core.management.base import BaseCommand

from routes.models import FuelStation, USCity


class Command(BaseCommand):
    help = "Link fuel stations to their US city"

    def handle(self, *args, **options):
        cities = {
            (city.city.lower(), city.state_id.lower()): city
            for city in USCity.objects.all()
        }

        matched = 0
        unmatched = 0

        for station in FuelStation.objects.all():
            key = (
                station.city.lower(),
                station.state.lower(),
            )

            city = cities.get(key)

            if city:
                station.city_location = city

                # Temporary coordinates based on city center.
                station.latitude = city.latitude
                station.longitude = city.longitude
                station.geocoding_source = "city_dataset"

                station.save(
                    update_fields=[
                        "city_location",
                        "latitude",
                        "longitude",
                        "geocoding_source",
                    ]
                )

                matched += 1
            else:
                unmatched += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Matched: {matched}"
            )
        )

        self.stdout.write(
            self.style.WARNING(
                f"Unmatched: {unmatched}"
            )
        )
        