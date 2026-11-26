import pygame


SIZE = (960, 620)
TANK = pygame.Rect(40, 46, 880, 528)


def fit_canvas(window_size: tuple[int, int]) -> pygame.Rect:
    width, height = window_size
    scale = min(width / SIZE[0], height / SIZE[1])
    fitted_width, fitted_height = max(1, round(SIZE[0] * scale)), max(1, round(SIZE[1] * scale))
    return pygame.Rect((width - fitted_width) // 2, (height - fitted_height) // 2, fitted_width, fitted_height)


def logical_point(point: tuple[int, int], frame: pygame.Rect) -> tuple[int, int]:
    x, y = point
    return (x - frame.left) * SIZE[0] // frame.width, (y - frame.top) * SIZE[1] // frame.height
