import requests
import numpy as np

from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import ConfigSerializer
from rest_framework.request import Request
from rest_framework import status as response_status
from django.apps import apps
from .utils.positions import xy_to_index, index_to_xy

from home import state


@api_view(['POST'])
def configure(request: Request) -> Response:
    """
    Configure the grid dimensions for image generation.
    """
    serializer = ConfigSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    state.CURRENT_IMAGE = {}
    state.CURRENT_X = 0
    state.CURRENT_Y = 0
    state.GRID_M = serializer.data.get('m')
    state.GRID_N = serializer.data.get('n')
    state.CURRENT_IMAGE_NP = np.zeros((state.GRID_M, state.GRID_N), dtype=np.uint8)

    return Response({"status": "configured", "m": state.GRID_M, "n": state.GRID_N}, status=response_status.HTTP_200_OK)


@api_view(['POST'])
def generate(request: Request) -> Response:
    """
    Generate image using original ping-pong method.
    
    Args:
        request: HTTP request with grid configuration {"m": int, "n": int}
        
    Returns:
        Response with generation results
    """

    if not state.GRID_M or not state.GRID_N:
        return Response({"error": "m and n are required"}, status=response_status.HTTP_400_BAD_REQUEST)
    
    try:
        response = requests.post(
            f"{apps.get_app_config('home').MAIN_URL}/ping/",
            json={
                "m": state.GRID_M,
                "n": state.GRID_N,
                "image": []
            },
            timeout=30
        )
        response.raise_for_status()
        
        return Response({
            'status': 'generation_started',
            'm': state.GRID_M,
            'n': state.GRID_N
        })
        
    except requests.exceptions.RequestException as e:
        print(f"Error starting generation: {e}")
        return Response({"error": str(e)}, status=response_status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def status(request: Request) -> Response:
    """
    Get the current status of image generation.
    """
    try:
        m = int(request.query_params.get('m', 0))
        n = int(request.query_params.get('n', 0))
    except (ValueError, TypeError):
        return Response({"error": "Invalid parameters"}, status=400)
    
    total_pixels = state.GRID_M * state.GRID_N
    if total_pixels <= 784:
        current_index = len(state.CURRENT_IMAGE)
        done = current_index >= total_pixels
        progress_percentage = (current_index / total_pixels * 100) if total_pixels > 0 else 0
    else:
        current_index = state.CURRENT_Y * state.GRID_N + state.CURRENT_X
        done = state.CURRENT_Y >= state.GRID_M
        progress_percentage = (current_index / total_pixels * 100) if total_pixels > 0 else 0
    
    return Response({
        "colored_pixels": current_index,
        "total_pixels": total_pixels,
        "done": done,
        "progress_percentage": progress_percentage,
        "current_position": (state.CURRENT_X, state.CURRENT_Y) if not done else None
    })


@api_view(['POST'])
def update_pixel(request: Request) -> Response:
    """
    Add a new pixel to the current image.
    Main service maintains the state while ping/pong remain stateless.
    """
    try:
        total_pixels = state.GRID_M * state.GRID_N

        if 'start_index' in request.data and 'end_index' in request.data:
            start_index = request.data['start_index']
            end_index = request.data['end_index']
            
            pixels_updated = 0
            for pixel_index in range(start_index, end_index):
                y = pixel_index // state.GRID_N
                x = pixel_index % state.GRID_N
                
                # Bounds check
                if 0 <= x < state.GRID_N and 0 <= y < state.GRID_M:
                    # Only update if pixel is not already set (avoid duplicates)
                    if state.CURRENT_IMAGE_NP[y, x] == 0:
                        state.CURRENT_IMAGE_NP[y, x] = 1
                        pixels_updated += 1

            
            state.CURRENT_X = end_index % state.GRID_N
            state.CURRENT_Y = end_index // state.GRID_N
            
            return Response({
                "status": "range_updated",
                "start_index": start_index,
                "end_index": end_index,
                "pixels_updated": pixels_updated,  # Actual new pixels, not range size
                "total_filled": int(np.sum(state.CURRENT_IMAGE_NP)),
                "total_pixels": total_pixels,
                "progress_percentage": (int(np.sum(state.CURRENT_IMAGE_NP)) / total_pixels * 100),
                "method": "range_update"
            }, status=response_status.HTTP_200_OK)
       
        # Handle single pixel updates (existing code for small/medium grids)
        pixel = request.data['pixel']
        x, y = pixel['x'], pixel['y']
        
        if total_pixels <= 784:
            color = tuple(pixel['color'])

            if state.CURRENT_IMAGE is None:
                state.CURRENT_IMAGE = {}
            
            if len(state.CURRENT_IMAGE) >= total_pixels:
                return Response({"status": "done"})
            
            if x >= state.GRID_N or y >= state.GRID_M:
                return Response({"status": "out_of_bounds"})
            
            index = xy_to_index(x, y, state.GRID_N)
            state.CURRENT_IMAGE[index] = color
        
            return Response({
                "status": "updated", 
                "total_pixels": len(state.CURRENT_IMAGE),
                "pixel": pixel
            }, status=response_status.HTTP_200_OK)
        else:
            if np.sum(state.CURRENT_IMAGE_NP) >= total_pixels:
                state.CURRENT_IMAGE = {}
            
            if x >= state.GRID_N or y >= state.GRID_M:
                return Response({"status": "out_of_bounds"})

            x, y = state.CURRENT_X, state.CURRENT_Y
            state.CURRENT_IMAGE_NP[y, x] = 1
            # Move to next position for next call
            state.CURRENT_X += 1
            if state.CURRENT_X >= state.GRID_N:
                state.CURRENT_X = 0
                state.CURRENT_Y += 1

            return Response({
                "status": "updated",
                "position": (x, y),
                "index": y * state.GRID_N + x,
                "next_position": (state.CURRENT_X, state.CURRENT_Y) if state.CURRENT_Y < state.GRID_M else None
            }, status=response_status.HTTP_200_OK)
    
    except Exception as e:
        print(f"Error updating pixel: {e}")
        return Response({"status": "error", "message": str(e)}, status=response_status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def ui_image(request: Request) -> Response:
    """
    Get the current image as JSON for the frontend.
    """
    total_pixels = state.GRID_M * state.GRID_N
    
    if total_pixels <= 784:
        image_list = []
        for index, color in state.CURRENT_IMAGE.items():
            x, y = index_to_xy(index, state.GRID_N)
            image_list.append({
                "x": x,
                "y": y, 
                "color": color
            })
        
        return Response({
            "image": image_list,
            "m": state.GRID_M,
            "n": state.GRID_N,
            "colored_pixels": len(state.CURRENT_IMAGE),
            "total_pixels": total_pixels
        })
    else:
        # For large grids, use range-based approach for better performance
        filled_positions = np.argwhere(state.CURRENT_IMAGE_NP == 1)
        
        if len(filled_positions) == 0:
            return Response({
                "image": [],
                "m": state.GRID_M,
                "n": state.GRID_N,
                "colored_pixels": 0,
                "total_pixels": total_pixels
            })
        
        # Remove duplicate positions to ensure unique pixels
        unique_positions = np.unique(filled_positions, axis=0)

        # Get all filled indices at once using vectorized operations
        y_coords = unique_positions[:, 0]
        x_coords = unique_positions[:, 1]
        color_indices = y_coords * state.GRID_N + x_coords

        # Calculate colors using sequential RGB generation (guaranteed unique)
        colors = np.zeros((len(color_indices), 3), dtype=np.uint8)

        # Generate truly unique sequential colors
        for i, idx in enumerate(color_indices):
            # Use base-256 encoding to ensure uniqueness
            colors[i] = [
                (idx // (256 * 256)) % 256,  # Red component
                (idx // 256) % 256,           # Green component  
                idx % 256                     # Blue component
            ]

        # Build image list using list comprehension (faster than loop)
        image_list = [
            {"x": int(x), "y": int(y), "color": color.tolist()}
            for x, y, color in zip(x_coords, y_coords, colors)
        ]

        return Response({
            "image": image_list,
            "m": state.GRID_M,
            "n": state.GRID_N,
            "colored_pixels": len(image_list),
            "total_pixels": total_pixels,
            "method": "sequential_unique_colors"
        })