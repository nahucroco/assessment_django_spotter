from routes.services.geocoding import GeocodingService


def geocode_route_candidates(candidates):
    geocoder = GeocodingService()

    updated = 0
    failed = 0

    for station, _ in candidates:
        # Ya intentamos geocodificar esta estación anteriormente.
        if station.geocoding_attempted:
            continue

        result = geocoder.geocode_station(
            name=station.name,
            address=station.address,
            city=station.city,
            state=station.state,
        )

        station.geocoding_attempted = True

        if result:
            station.latitude = result["latitude"]
            station.longitude = result["longitude"]
            station.geocoding_source = result["source"]

            station.save(
                update_fields=[
                    "latitude",
                    "longitude",
                    "geocoding_source",
                    "geocoding_attempted",
                ]
            )

            updated += 1

        else:
            station.save(
                update_fields=["geocoding_attempted"]
            )
            failed += 1

    return updated, failed