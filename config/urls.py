from django.contrib import admin
from django.urls import include, path
from routes.views import route_demo


urlpatterns = [
    path("demo/", route_demo, name="route-demo"),
    path("admin/", admin.site.urls),
    path("api/", include("routes.urls")),
]