import csv
from pathlib import Path

from django.core.management.base import BaseCommand

from routes.models import FuelStation


US_STATES = {
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
    "DC",
}


class Command(BaseCommand):
    help = "Import and consolidate fuel stations from the assessment CSV"

    def handle(self, *args, **options):
        csv_path = (
            Path(__file__).resolve().parents[3]
            / "data"
            / "fuel-prices-for-be-assessment.csv"
        )

        if not csv_path.exists():
            self.stderr.write(
                self.style.ERROR(f"CSV not found: {csv_path}")
            )
            return

        stations = {}

        with csv_path.open(
            mode="r",
            encoding="utf-8-sig",
            newline="",
        ) as file:
            reader = csv.DictReader(file)

            for row in reader:
                state = row["State"].strip()

                # Only import stations located in the USA.
                if state not in US_STATES:
                    continue

                opis_id = int(row["OPIS Truckstop ID"])
                price = float(row["Retail Price"])

                station = stations.get(opis_id)

                # Keep the cheapest price for each physical station.
                if station is None or price < station["price"]:
                    stations[opis_id] = {
                        "opis_id": opis_id,
                        "name": row["Truckstop Name"].strip(),
                        "address": row["Address"].strip(),
                        "city": row["City"].strip(),
                        "state": state,
                        "rack_id": int(row["Rack ID"]),
                        "price": price,
                    }

        FuelStation.objects.all().delete()

        FuelStation.objects.bulk_create(
            FuelStation(**station)
            for station in stations.values()
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully imported {len(stations)} unique US fuel stations."
            )
        )