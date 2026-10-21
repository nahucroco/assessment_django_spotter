from requests import RequestException
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from routes.serializers import RouteRequestSerializer
from routes.services.route_planning import RoutePlanningService



class RoutePlanningView(APIView):

    def post(self, request):
        serializer = RouteRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        start = (
            serializer.validated_data["start"]["longitude"],
            serializer.validated_data["start"]["latitude"],
        )

        finish = (
            serializer.validated_data["finish"]["longitude"],
            serializer.validated_data["finish"]["latitude"],
        )

        service = RoutePlanningService()

        try:
            result = service.plan_route(
                start=start,
                finish=finish,
            )

        except RequestException:
            return Response(
                {
                    "error": "Unable to calculate the route."
                },
                status=status.HTTP_502_BAD_GATEWAY,
            )

        except ValueError as error:
            return Response(
                {
                    "error": str(error)
                },
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        return Response(
            {
                "route": {
                    "distance_miles": round(
                        result["route_distance_miles"],
                        2,
                    ),
                    "geometry": result["route_points"],
                },
                "fuel": {
                    "total_cost": round(
                        result["total_fuel_cost"],
                        2,
                    ),
                    "stops": [
                        {
                            "station": stop.station.name,
                            "location": {
                                "latitude": stop.station.latitude,
                                "longitude": stop.station.longitude,
                            },
                            "city": stop.station.city,
                            "state": stop.station.state,
                            "price_per_gallon": float(
                                stop.station.price
                            ),
                            "distance_from_start_miles": round(
                                stop.distance_from_start,
                                2,
                            ),
                            "gallons": round(
                                stop.gallons,
                                2,
                            ),
                            "cost": round(
                                stop.cost,
                                2,
                            ),
                        }
                        for stop in result["fuel_stops"]
                    ],
                },
            },
            status=status.HTTP_200_OK,
        )

@ensure_csrf_cookie
def route_demo(request):
    """Render a small browser UI for the existing route-planning API."""
    return render(request, "routes/demo.html")
