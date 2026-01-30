from abc import ABC, abstractmethod
from rest_framework.request import Request
from rest_framework.response import Response


class ImageGenerationStrategy(ABC):
    min_pixels: int
    max_pixels: int | None

    def supports(self, total_pixels: int) -> bool:
        if self.max_pixels is None:
            return total_pixels >= self.min_pixels
        return self.min_pixels <= total_pixels <= self.max_pixels

    @abstractmethod
    def handle(self, request: Request, next_url: str) -> Response:
        pass
