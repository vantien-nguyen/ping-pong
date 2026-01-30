import random

def random_unique_color(used_colors):
    while True:
        color = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
        if color not in used_colors:
            return color
