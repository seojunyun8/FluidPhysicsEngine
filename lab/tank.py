from math import hypot

import pygame

from engine.rigid import CircleBody
from engine.world import World

from .layout import TANK


def blend(first: tuple[int, int, int], second: tuple[int, int, int], amount: float) -> tuple[int, int, int]:
    return tuple(round(low + (high - low) * amount) for low, high in zip(first, second))


class Tank:
    def __init__(self, mono: pygame.font.Font) -> None:
        self.base = pygame.Surface(TANK.size)
        self.layer = pygame.Surface(TANK.size)
        self.mono = mono
        for y in range(TANK.height):
            color = blend((13, 33, 52), (16, 48, 65), y / TANK.height)
            pygame.draw.line(self.base, color, (0, y), (TANK.width, y))
        for x in range(70, TANK.width, 70):
            pygame.draw.line(self.base, (27, 56, 73), (x, 0), (x, TANK.height))
        for y in range(70, TANK.height, 70):
            pygame.draw.line(self.base, (27, 56, 73), (0, y), (TANK.width, y))
        for x in range(0, TANK.width, 35):
            pygame.draw.line(self.base, (62, 90, 105), (x, 0), (x, 7 if x % 70 == 0 else 4))
        for y in range(0, TANK.height, 35):
            pygame.draw.line(self.base, (62, 90, 105), (0, y), (7 if y % 70 == 0 else 4, y))
        self.flow_colors = [blend((24, 170, 205), (164, 248, 235), level / 31) for level in range(32)]
        self.pressure_colors = [blend((43, 134, 224), (255, 196, 102), level / 31) for level in range(32)]

    def draw(
        self, canvas: pygame.Surface, world: World, pressure: bool, pointer: tuple[int, int],
        brush: bool, emitter: bool,
    ) -> None:
        self.layer.blit(self.base, (0, 0))
        scale = TANK.width / world.settings.width
        palette = self.pressure_colors if pressure else self.flow_colors
        for particle in world.particles:
            x, y = round(particle.x * scale), round(particle.y * scale)
            speed = hypot(particle.vx, particle.vy)
            magnitude = particle.pressure / 37.0 if pressure else 0.18 + speed / 11.0
            color = palette[min(31, int(magnitude * 31))]
            if not pressure and speed > 2.8:
                tail = (x - round(particle.vx * 1.7), y - round(particle.vy * 1.7))
                pygame.draw.line(self.layer, (37, 102, 126), (x, y), tail, 2)
            pygame.draw.circle(self.layer, (18, 77, 103), (x, y), 10)
            pygame.draw.circle(self.layer, color, (x, y), 7)
            pygame.draw.circle(self.layer, blend(color, (207, 253, 250), 0.33), (x - 2, y - 2), 2)

        for body in world.bodies:
            self._draw_body(body, scale)

        if TANK.collidepoint(pointer) and (brush or emitter):
            x, y = pointer[0] - TANK.x, pointer[1] - TANK.y
            radius = round(0.85 * scale) if brush else 19
            pygame.draw.circle(self.layer, (224, 247, 250), (x, y), radius, 1)
            pygame.draw.circle(self.layer, (224, 247, 250), (x, y), 3)

        pygame.draw.rect(self.layer, (56, 88, 107), self.layer.get_rect(), 1, border_radius=10)
        canvas.blit(self.layer, TANK.topleft)

    def _draw_body(self, body: CircleBody, scale: float) -> None:
        x, y = round(body.x * scale), round(body.y * scale)
        radius = round(body.radius * scale)
        if body.fixed:
            edge, fill, inner = (112, 148, 168), (26, 57, 75), (52, 81, 99)
        elif body.name == "Light":
            edge, fill, inner = (255, 200, 125), (118, 77, 43), (157, 105, 58)
        else:
            edge, fill, inner = (218, 172, 245), (76, 51, 106), (105, 74, 136)

        pygame.draw.circle(self.layer, (11, 28, 41), (x + 2, y + 3), radius + 2)
        pygame.draw.circle(self.layer, fill, (x, y), radius)
        pygame.draw.circle(self.layer, inner, (x, y), radius - 6, 1)
        pygame.draw.circle(self.layer, edge, (x, y), radius, 2)
        if body.surface_y is not None and 0.0 < body.submerged < 1.0:
            waterline = round(body.surface_y * scale)
            half_width = int(max(0, radius * radius - (waterline - y) ** 2) ** 0.5)
            pygame.draw.line(self.layer, inner, (x - half_width, waterline), (x + half_width, waterline), 2)
        label = self.mono.render(body.name.upper(), True, edge)
        self.layer.blit(label, label.get_rect(center=(x, y)))
