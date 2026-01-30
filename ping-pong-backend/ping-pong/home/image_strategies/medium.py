import requests
from django.apps import apps
from rest_framework.response import Response

from home.image_strategies.base import ImageGenerationStrategy

from home import state

class MediumImageStrategy(ImageGenerationStrategy):
    min_pixels = 785
    max_pixels = 10_000

    def handle(self, request, next_url):
        current_index = state.CURRENT_Y * state.GRID_N + state.CURRENT_X

        # Check if done
        if current_index >= state.GRID_M * state.GRID_N:
            return Response({"status": "done"})
        
        # Store current position for response
        current_x, current_y = state.CURRENT_X, state.CURRENT_Y
        
        # Update main service with current pixel
        try:
            requests.post(
                f"{apps.get_app_config('home').MAIN_URL}/status/update_pixel/",
                json={"pixel": {"x": current_x, "y": current_y}},
                timeout=2
            )
        except:
            pass

        # Send to next service
        payload = {
            "m": state.GRID_M, 
            "n": state.GRID_N, 
            "position": (current_x, current_y),
            "index": current_index
        }

        requests.post(next_url, json=payload, timeout=30)

        return Response({
            "status": "pixel_added",
            "position": (current_x, current_y),
            "index": current_index,
            "method": "medium_sequential"
        })
