import csv
from pathlib import Path

from django.core.management.base import BaseCommand

from routes.models import USCity


class Command(BaseCommand):
    help = "Import US cities with coordinates"

    def handle(self, *args, **options):
        csv_path = (
            Path(__file__).resolve().parents[3]
            / "data"
            / "uscities.csv"
        )

        cities = []

        with csv_path.open(
            "r",
            encoding="utf-8-sig",
            newline="",
        ) as file:
            reader = csv.DictReader(file)

            for row in reader:
                cities.append(
                    USCity(
                        city=row["city"],
                        state_id=row["state_id"],
                        state_name=row["state_name"],
                        latitude=float(row["lat"]),
                        longitude=float(row["lng"]),
                    )
                )

        USCity.objects.bulk_create(
            cities,
            ignore_conflicts=True,
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Imported {len(cities)} US cities."
            )
        )