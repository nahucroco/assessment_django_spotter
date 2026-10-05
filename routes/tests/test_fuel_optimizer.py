from types import SimpleNamespace

from django.test import SimpleTestCase

from routes.services.fuel_optimizer import optimize_fuel_stops


def station(name, price):
    return SimpleNamespace(
        name=name,
        price=price,
    )


class FuelOptimizerTests(SimpleTestCase):

    def test_route_that_needs_no_stop(self):
        candidates = []

        stops, total_cost = optimize_fuel_stops(
            candidates=candidates,
            route_distance=300,
        )

        self.assertEqual(stops, [])
        self.assertEqual(total_cost, 0)

    def test_route_that_needs_one_stop(self):
        cheap_station = station("Cheap Station", 3.00)

        candidates = [
            (cheap_station, 0, 300),
        ]

        stops, total_cost = optimize_fuel_stops(
            candidates=candidates,
            route_distance=700,
        )

        self.assertEqual(len(stops), 1)
        self.assertEqual(stops[0].station.name, "Cheap Station")
        self.assertAlmostEqual(stops[0].gallons, 20.0)
        self.assertAlmostEqual(total_cost, 60.0)

    def test_prefers_cheaper_station_within_range(self):
        expensive = station("Expensive", 4.00)
        cheap = station("Cheap", 2.00)

        candidates = [
            (expensive, 0, 200),
            (cheap, 0, 400),
        ]

        stops, total_cost = optimize_fuel_stops(
            candidates=candidates,
            route_distance=700,
        )

        self.assertEqual(len(stops), 1)
        self.assertEqual(stops[0].station.name, "Cheap")
        self.assertAlmostEqual(total_cost, 40.0)

    def test_route_with_multiple_stops(self):
        station_a = station("Station A", 3.00)
        station_b = station("Station B", 2.50)
        station_c = station("Station C", 3.00)

        candidates = [
            (station_a, 0, 400),
            (station_b, 0, 800),
            (station_c, 0, 1200),
        ]

        stops, total_cost = optimize_fuel_stops(
            candidates=candidates,
            route_distance=1400,
        )

        self.assertGreaterEqual(len(stops), 2)
        self.assertGreater(total_cost, 0)

    def test_raises_error_when_next_station_is_unreachable(self):
        station_a = station("Station A", 3.00)

        candidates = [
            (station_a, 0, 600),
        ]

        with self.assertRaises(ValueError):
            optimize_fuel_stops(
                candidates=candidates,
                route_distance=1000,
            )

    def test_minimizes_cost_when_cheaper_station_is_available(self):
        expensive = station("Expensive", 4.00)
        cheap = station("Cheap", 2.00)
        final = station("Final", 3.00)
        candidates = [
            (expensive, 0, 200),
            (cheap, 0, 400),
            (final, 0, 800),
        ]
        stops, total_cost = optimize_fuel_stops(
            candidates=candidates,
            route_distance=1000,
        )
        self.assertEqual(
            [stop.station.name for stop in stops],
            ["Cheap", "Final"],
        )
        self.assertEqual(
            stops[0].station.name,
            "Cheap",
        )

        self.assertNotIn(
            "Expensive",
            [stop.station.name for stop in stops],
        )
