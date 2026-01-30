from django.urls import include, path

urlpatterns = [
    path("api/", include("home.urls")),
    path("api/", include("ping.urls")),
    path("api/", include("pong.urls")),
]
