from math import hypot

from .particles import Particle
from .rigid import CircleBody
from .settings import Settings


def keep_in_tank(
    item: Particle | CircleBody, settings: Settings, *, radius: float | None = None,
) -> None:
    radius = settings.particle_radius if radius is None else radius
    right = settings.width - radius
    bottom = settings.height - radius
    bounce = 0.22

    if item.x < radius:
        item.x = radius
        item.vx = max(0.0, -bounce * item.vx)
    elif item.x > right:
        item.x = right
        item.vx = min(0.0, -bounce * item.vx)

    if item.y < radius:
        item.y = radius
        item.vy = max(0.0, -bounce * item.vy)
    elif item.y > bottom:
        item.y = bottom
        item.vy = min(0.0, -bounce * item.vy)


def collide_with_circle(
    first: Particle | CircleBody, second: CircleBody, limit: float, first_inverse_mass: float,
) -> bool:
    dx, dy = first.x - second.x, first.y - second.y
    distance = hypot(dx, dy)
    if distance >= limit:
        return False

    nx, ny = (dx / distance, dy / distance) if distance > 1e-10 else (0.0, 1.0)
    second_inverse_mass = second.inverse_mass
    inverse_mass_sum = first_inverse_mass + second_inverse_mass
    correction = (limit - distance) / inverse_mass_sum
    first.x += nx * correction * first_inverse_mass
    first.y += ny * correction * first_inverse_mass
    second.x -= nx * correction * second_inverse_mass
    second.y -= ny * correction * second_inverse_mass

    relative_speed = (first.vx - second.vx) * nx + (first.vy - second.vy) * ny
    if relative_speed < 0:
        impulse = -1.15 * relative_speed / inverse_mass_sum
        first.vx += nx * impulse * first_inverse_mass
        first.vy += ny * impulse * first_inverse_mass
        second.vx -= nx * impulse * second_inverse_mass
        second.vy -= ny * impulse * second_inverse_mass
    return True
