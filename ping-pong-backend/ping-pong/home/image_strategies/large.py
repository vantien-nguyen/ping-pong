import requests
import numpy as np
from django.apps import apps
from rest_framework.response import Response

from home.image_strategies.base import ImageGenerationStrategy
from home import state


class LargeImageStrategy(ImageGenerationStrategy):
    min_pixels = 10_001
    max_pixels = 20_000_000

    def handle(self, request, next_url):
        data = request.data
        m = data['m']
        n = data['n']
        
        # Get current position from state
        current_index = state.CURRENT_Y * state.GRID_N + state.CURRENT_X
        total_pixels = state.GRID_M * state.GRID_N
        
        # Check if done
        if current_index >= total_pixels:
            return Response({"status": "done"})
        
        # Calculate batch size based on grid size (optimized for up to 20M pixels)
        if total_pixels >= 10_000_000:
            batch_size = 2_000_000  # 2M pixels for massive grids (10 requests for 20M)
        elif total_pixels >= 4_000_000:
            batch_size = 1_000_000  # 1M pixels for huge grids (20 requests for 20M)
        elif total_pixels >= 1_000_000:
            batch_size = 500_000    # 500K pixels for large grids (40 requests for 20M)
        elif total_pixels >= 100_000:
            batch_size = 100_000    # 100K pixels for medium-large grids
        else:
            batch_size = 50_000     # 50K pixels for smaller grids
        
        # Calculate remaining pixels
        remaining_pixels = total_pixels - current_index
        actual_batch_size = min(batch_size, remaining_pixels)
        
        # Generate batch of pixels
        pixels_batch = []
        for i in range(actual_batch_size):
            pixel_index = current_index + i
            
            # Safety check - don't exceed total pixels
            if pixel_index >= total_pixels:
                break
                
            y = pixel_index // state.GRID_N
            x = pixel_index % state.GRID_N
            
            # Additional bounds check
            if y >= state.GRID_M or x >= state.GRID_N:
                break
            
            pixels_batch.append({
                "x": x,
                "y": y,
                "index": pixel_index
            })
        
        # Update state for next batch
        new_current_index = current_index + len(pixels_batch)
        
        # Update main service with batch (sample for performance)
        try:
            requests.post(
                f"{apps.get_app_config('home').MAIN_URL}/status/update_pixel/",
                json={
                    "start_index": current_index,
                    "end_index": new_current_index
                },
                timeout=2
            )
        except:
            pass
        
        # Send batch to next service
        payload = {
            "m": m,
            "n": n,
            "batch": pixels_batch,
            "batch_size": actual_batch_size,
            "current_index": current_index,
            "method": "large_batch_sequential"
        }
        
        requests.post(next_url, json=payload, timeout=30)
        
        return Response({
            "status": "batch_added",
            "batch_size": actual_batch_size,
            "current_index": current_index,
            "next_index": new_current_index,
            "progress_percentage": (new_current_index / total_pixels * 100),
            "method": "large_batch_sequential"
        })