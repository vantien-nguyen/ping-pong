from home.image_strategies.small import SmallImageStrategy
from home.image_strategies.medium import MediumImageStrategy
from home.image_strategies.large import LargeImageStrategy

STRATEGIES = [
    SmallImageStrategy(),
    MediumImageStrategy(),
    LargeImageStrategy(),
]


def get_image_strategy(total_pixels: int):
    for strategy in STRATEGIES:
        if strategy.supports(total_pixels):
            return strategy
    raise ValueError(f"No strategy for total_pixels={total_pixels}")
