import random


def random_empty_position(m, n, image):
    empty = [(x, y) for x in range(m) for y in range(n) if (x, y) not in image]
    return random.choice(empty)


def xy_to_index(x: int, y: int, n: int) -> int:
    """
    Convert (x, y) coordinates to linear index for any grid size.
    
    Args:
        x: x coordinate (column)
        y: y coordinate (row) 
        n: grid width (number of columns)
    
    Returns:
        Linear index: y * n + x
    """
    return y * n + x

def index_to_xy(index: int, n: int) -> tuple[int, int]:
    """
    Convert linear index to (x, y) coordinates for any grid size.
    
    Args:
        index: Linear index
        n: Grid width (number of columns)
    
    Returns:
        Tuple (x, y) coordinates
    """
    y = index // n  # Row
    x = index % n   # Column
    return x, y
