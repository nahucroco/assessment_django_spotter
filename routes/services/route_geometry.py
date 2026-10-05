import math

import polyline
from shapely.geometry import LineString, Point


EARTH_RADIUS_MILES = 3958.8
MILES_PER_DEGREE_LAT = 69.0


def haversine_distance(point_a, point_b):
    lat1, lon1 = point_a
    lat2, lon2 = point_b

    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)

    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(delta_lon / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return EARTH_RADIUS_MILES * c


def decode_route_geometry(encoded_geometry):
    return polyline.decode(encoded_geometry)


def create_route_line(route_points):
    reference_latitude = sum(
        latitude for latitude, _ in route_points
    ) / len(route_points)

    miles_per_degree_lon = (
        MILES_PER_DEGREE_LAT
        * math.cos(math.radians(reference_latitude))
    )

    def to_xy(latitude, longitude):
        return (
            longitude * miles_per_degree_lon,
            latitude * MILES_PER_DEGREE_LAT,
        )

    route_xy = [
        to_xy(latitude, longitude)
        for latitude, longitude in route_points
    ]

    return LineString(route_xy), to_xy


def distance_to_route(station, route_line, to_xy):
    latitude, longitude = station

    station_point = Point(
        to_xy(latitude, longitude)
    )

    return station_point.distance(route_line)


def find_stations_near_route(
    stations,
    route_points,
    max_distance_miles=5.0,
):
    route_line, to_xy = create_route_line(route_points)

    min_x, min_y, max_x, max_y = route_line.bounds

    candidates = []

    for station in stations:
        if station.latitude is None or station.longitude is None:
            continue

        station_x, station_y = to_xy(
            station.latitude,
            station.longitude,
        )

        # Bounding box filter.
        if (
            station_x < min_x - max_distance_miles
            or station_x > max_x + max_distance_miles
            or station_y < min_y - max_distance_miles
            or station_y > max_y + max_distance_miles
        ):
            continue

        distance = distance_to_route(
            (station.latitude, station.longitude),
            route_line,
            to_xy,
        )

        if distance <= max_distance_miles:
            candidates.append((station, distance))

    candidates.sort(key=lambda item: item[1])

    return candidates


def calculate_route_distances(route_points):
    distances = [0.0]

    for previous, current in zip(
        route_points,
        route_points[1:],
    ):
        segment_distance = haversine_distance(
            previous,
            current,
        )

        distances.append(
            distances[-1] + segment_distance
        )

    return distances


def locate_station_on_route(
    station,
    route_points,
    route_distances,
):
    route_line, to_xy = create_route_line(route_points)

    latitude, longitude = station

    station_point = Point(
        to_xy(latitude, longitude)
    )

    projected_distance = route_line.project(
        station_point
    )

    route_length = route_line.length

    if route_length == 0:
        return 0.0

    ratio = projected_distance / route_length

    return ratio * route_distances[-1]


def prepare_route_candidates(
    candidates,
    route_points,
    route_distances,
):
    route_line, to_xy = create_route_line(route_points)

    prepared = []

    for station, distance_to_route in candidates:
        latitude = station.latitude
        longitude = station.longitude

        station_point = Point(
            to_xy(latitude, longitude)
        )

        projected_distance = route_line.project(
            station_point
        )

        route_length = route_line.length

        if route_length == 0:
            distance_from_start = 0.0
        else:
            ratio = (
                projected_distance
                / route_length
            )

            distance_from_start = (
                ratio * route_distances[-1]
            )

        prepared.append(
            (
                station,
                distance_to_route,
                distance_from_start,
            )
        )

    return prepared

def get_route_bounding_box(
    route_points,
    max_distance_miles=5.0,
):
    latitudes = [point[0] for point in route_points]
    longitudes = [point[1] for point in route_points]

    min_lat = min(latitudes)
    max_lat = max(latitudes)
    min_lon = min(longitudes)
    max_lon = max(longitudes)

    reference_latitude = (
        min_lat + max_lat
    ) / 2

    lat_margin = (
        max_distance_miles
        / MILES_PER_DEGREE_LAT
    )

    miles_per_degree_lon = (
        MILES_PER_DEGREE_LAT
        * math.cos(
            math.radians(reference_latitude)
        )
    )

    lon_margin = (
        max_distance_miles
        / miles_per_degree_lon
    )

    return (
        min_lat - lat_margin,
        max_lat + lat_margin,
        min_lon - lon_margin,
        max_lon + lon_margin,
    )