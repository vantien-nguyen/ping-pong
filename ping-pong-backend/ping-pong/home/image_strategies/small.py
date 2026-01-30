import requests
from django.apps import apps
from rest_framework.response import Response

from home.image_strategies.base import ImageGenerationStrategy
from home.utils.positions import random_empty_position
from home.utils.colors import random_unique_color


class SmallImageStrategy(ImageGenerationStrategy):
    min_pixels = 0
    max_pixels = 784

    def handle(self, request, next_url):
        data = request.data
        m = data['m']
        n = data['n']

        image_data = data.get('image', [])
        image = {(p['x'], p['y']): tuple(p['color']) for p in image_data}
        used_colors = set(image.values())

        if len(image) >= m * n:
            return Response({"status": "done"})

        (x, y) = random_empty_position(m, n, image)
        color = random_unique_color(used_colors)
        image[(x, y)] = color

        try:
            requests.post(
                f"{apps.get_app_config('home').MAIN_URL}/status/update_pixel/",
                json={"pixel": {"x": x, "y": y, "color": list(color)}, "n": n},
                timeout=2
            )
        except:
            pass

        new_image = [{"x": px, "y": py, "color": list(pc)} for (px, py), pc in image.items()]
        payload = {"m": m, "n": n, "image": new_image}

        requests.post(next_url, json=payload, timeout=30)

        return Response({
            "status": "pixel_added",
            "pixel": {"x": x, "y": y, "color": list(color)},
            "method": "small_random"
        })
