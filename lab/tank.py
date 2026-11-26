import pygame

from engine.world import World

from .layout import TANK


WATER_FILL = (20, 72, 116)
WATER_SHADES = tuple((41 + i * 3, 124 + i * 3, 181 + i * 2) for i in range(16))


def draw_tank(canvas: pygame.Surface, world: World) -> None:
    settings = world.settings
    scale = TANK.width / settings.width
    radius = max(1, round(settings.particle_radius * scale))
    fill_radius = round(settings.spacing * 0.72 * scale)
    dense_limit = settings.rest_density * 0.70

    canvas.fill((0, 0, 0))
    canvas.set_clip(TANK)
    spots = []
    for particle in world.particles:
        center = (TANK.x + round(particle.x * scale), TANK.y + round(particle.y * scale))
        spots.append((particle, center))
        # Overlap the dense part of the water while keeping spray separate.
        if particle.density >= dense_limit:
            pygame.draw.circle(canvas, WATER_FILL, center, fill_radius)

    for particle, center in spots:
        speed_squared = particle.vx * particle.vx + particle.vy * particle.vy
        shade = WATER_SHADES[min(len(WATER_SHADES) - 1, int(speed_squared * 0.43))]
        pygame.draw.circle(canvas, shade, center, radius)

    for body in world.bodies:
        center = (TANK.x + round(body.x * scale), TANK.y + round(body.y * scale))
        body_radius = round(body.radius * scale)
        pygame.draw.circle(canvas, (221, 134, 60), center, body_radius)
        pygame.draw.circle(canvas, (255, 201, 130), center, body_radius, 2)

    canvas.set_clip(None)
    pygame.draw.rect(canvas, (145, 150, 158), TANK, 1)
