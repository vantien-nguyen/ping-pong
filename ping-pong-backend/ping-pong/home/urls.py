from django.urls import path
from home.views import configure, generate, status, ui_image, update_pixel

urlpatterns = [
    path("configure/", configure),
    path("generate/", generate),
    path("status/", status),
    path("ui/", ui_image),
    path("status/update_pixel/", update_pixel),
]
