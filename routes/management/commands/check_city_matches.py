from django.core.management.base import BaseCommand

from routes.models import FuelStation, USCity


class Command(BaseCommand):
    help = "Check how many fuel stations match a US city"

    def handle(self, *args, **options):
        cities = {
            (city.city.lower(), city.state_id.lower())
            for city in USCity.objects.all()
        }

        matched = 0
        unmatched = 0

        for station in FuelStation.objects.all():
            key = (
                station.city.lower(),
                station.state.lower(),
            )

            if key in cities:
                matched += 1
            else:
                unmatched += 1

        self.stdout.write(
            f"Matched: {matched}"
        )
        self.stdout.write(
            f"Unmatched: {unmatched}"
        )
        