from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response
from django.apps import apps

from home.image_strategies.registry import get_image_strategy


@api_view(['POST'])
def ping(request: Request) -> Response:
    data = request.data

    m = int(data.get('m', 0))
    n = int(data.get('n', 0))
    total_pixels = m * n

    pong_url = f"{apps.get_app_config('home').MAIN_URL}/pong/"
    strategy = get_image_strategy(total_pixels)

    return strategy.handle(request, pong_url)
