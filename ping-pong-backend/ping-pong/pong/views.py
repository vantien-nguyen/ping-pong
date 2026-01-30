from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response
from django.apps import apps

from home.image_strategies.registry import get_image_strategy


@api_view(['POST'])
def pong(request: Request) -> Response:
    data = request.data

    m = int(data.get('m', 0))
    n = int(data.get('n', 0))
    total_pixels = m * n

    ping_url = f"{apps.get_app_config('home').MAIN_URL}/ping/"
    strategy = get_image_strategy(total_pixels)

    return strategy.handle(request, ping_url)
