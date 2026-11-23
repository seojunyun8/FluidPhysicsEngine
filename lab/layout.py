import pygame


SIZE = (1200, 770)
TANK = pygame.Rect(28, 144, 840, 504)
PANEL = pygame.Rect(890, 96, 282, 618)

BUTTONS = {
    "dam": pygame.Rect(28, 96, 143, 36),
    "float": pygame.Rect(179, 96, 143, 36),
    "pause": pygame.Rect(947, 32, 108, 38),
    "reset": pygame.Rect(1063, 32, 109, 38),
    "flow": pygame.Rect(909, 387, 120, 34),
    "pressure": pygame.Rect(1033, 387, 120, 34),
    "buoyancy": pygame.Rect(909, 473, 244, 36),
}


def fit_canvas(window_size: tuple[int, int]) -> pygame.Rect:
    width, height = window_size
    scale = min(width / SIZE[0], height / SIZE[1])
    fitted_width, fitted_height = max(1, round(SIZE[0] * scale)), max(1, round(SIZE[1] * scale))
    return pygame.Rect((width - fitted_width) // 2, (height - fitted_height) // 2, fitted_width, fitted_height)


def logical_point(point: tuple[int, int], frame: pygame.Rect) -> tuple[int, int]:
    x, y = point
    return (x - frame.left) * SIZE[0] // frame.width, (y - frame.top) * SIZE[1] // frame.height
