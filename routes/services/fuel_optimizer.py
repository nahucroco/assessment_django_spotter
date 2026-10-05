from dataclasses import dataclass


TANK_CAPACITY_GALLONS = 50.0
FUEL_EFFICIENCY_MPG = 10.0
MAX_RANGE_MILES = 500.0
MIN_FUEL_PURCHASE_GALLONS = 0.01


@dataclass
class FuelStop:
    station: object
    distance_from_start: float
    gallons: float
    cost: float


def optimize_fuel_stops(
    candidates: list[tuple[object, float, float]],
    route_distance: float,
) -> tuple[list[FuelStop], float]:
    """
    Find the cost-effective fuel stops for a route.

    candidates contains:
        (station, distance_to_route, distance_from_start)

    The vehicle starts with a full tank.
    """

    candidates = sorted(
        candidates,
        key=lambda item: item[2],
    )

    stops = []
    total_cost = 0.0

    fuel = TANK_CAPACITY_GALLONS
    current_position = 0.0

    for index, (station, _, station_position) in enumerate(candidates):

        distance_to_station = (
            station_position - current_position
        )

        available_range = fuel * FUEL_EFFICIENCY_MPG

        if distance_to_station > available_range + 0.01:
            raise ValueError(
                f"Cannot reach next fuel station. "
                f"Current position: {current_position:.2f} miles, "
                f"next station: {station_position:.2f} miles, "
                f"distance: {distance_to_station:.2f} miles, "
                f"available range: {fuel * FUEL_EFFICIENCY_MPG:.2f} miles."
            )

        fuel -= distance_to_station / FUEL_EFFICIENCY_MPG

        remaining_distance = (
            route_distance - station_position
        )

        if remaining_distance <= 0:
            break

        # Find the first cheaper station that can be reached.
        cheaper_station = None

        for next_station, _, next_position in candidates[index + 1:]:
            distance = next_position - station_position

            if distance > MAX_RANGE_MILES:
                break

            if next_station.price < station.price:
                cheaper_station = (
                    next_station,
                    next_position,
                )
                break

        if cheaper_station:
            target_position = cheaper_station[1]
        else:
            target_position = min(
                station_position + MAX_RANGE_MILES,
                route_distance,
            )

        distance_to_target = (
            target_position - station_position
        )

        required_gallons = (
            distance_to_target / FUEL_EFFICIENCY_MPG
        )

        gallons_to_buy = max(
            0.0,
            required_gallons - fuel,
        )

        gallons_to_buy = min(
            gallons_to_buy,
            TANK_CAPACITY_GALLONS - fuel,
        )

        if gallons_to_buy >= MIN_FUEL_PURCHASE_GALLONS:
            cost = gallons_to_buy * float(station.price)

            fuel += gallons_to_buy
            total_cost += cost

            stops.append(
                FuelStop(
                    station=station,
                    distance_from_start=station_position,
                    gallons=gallons_to_buy,
                    cost=cost,
                )
            )

        current_position = station_position

    return stops, total_cost