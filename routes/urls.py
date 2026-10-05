from django.urls import path

from routes.views import RoutePlanningView


urlpatterns = [
    path(
        "routes/",
        RoutePlanningView.as_view(),
        name="route-planning",
    ),
]