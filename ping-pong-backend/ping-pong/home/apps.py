from django.apps import AppConfig
import os


class HomeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "home"

    MAIN_URL = os.getenv("MAIN_URL", "http://localhost:8000/api")
