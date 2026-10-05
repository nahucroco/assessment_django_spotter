from routes.models import FuelStation
from routes.services.fuel_optimizer import optimize_fuel_stops
from routes.services.route_geometry import (
    calculate_route_distances,
    decode_route_geometry,
    find_stations_near_route,
    get_route_bounding_box,
    prepare_route_candidates,
)
from routes.services.routing import RoutingService


class RoutePlanningService:

    def __init__(self):
        self.routing_service = RoutingService()

    def plan_route(
        self,
        start: tuple[float, float],
        finish: tuple[float, float],
    ) -> dict:
        route = self.routing_service.get_route(start, finish)

        route_data = route["routes"][0]

        route_points = decode_route_geometry(
            route_data["geometry"]
        )

        route_distances = calculate_route_distances(
            route_points
        )

        route_distance = route_distances[-1]

        min_lat, max_lat, min_lon, max_lon = (
            get_route_bounding_box(
                route_points,
                max_distance_miles=5,
            )
        )
        
        stations = FuelStation.objects.filter(
            latitude__isnull=False,
            longitude__isnull=False,
            latitude__gte=min_lat,
            latitude__lte=max_lat,
            longitude__gte=min_lon,
            longitude__lte=max_lon,
        )
        
        candidates = find_stations_near_route(
            stations,
            route_points,
            max_distance_miles=5,
        )

        prepared_candidates = prepare_route_candidates(
            candidates,
            route_points,
            route_distances,
        )

        stops, total_cost = optimize_fuel_stops(
            prepared_candidates,
            route_distance,
        )

        return {
            "route_points": route_points,
            "route_distance_miles": route_distance,
            "fuel_stops": stops,
            "total_fuel_cost": total_cost,
        }