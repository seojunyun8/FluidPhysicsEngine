from math import hypot, sqrt

from .particles import Particle
from .rigid import CircleBody
from .settings import Settings


def keep_in_tank(item: Particle | CircleBody, radius: float, settings: Settings, bounce: float) -> None:
    right = settings.width - radius
    bottom = settings.height - radius
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


def separate_bodies(first: CircleBody, second: CircleBody) -> None:
    dx, dy = first.x - second.x, first.y - second.y
    distance = hypot(dx, dy)
    penetration = first.radius + second.radius - distance
    first_inverse, second_inverse = first.inverse_mass, second.inverse_mass
    inverse_mass = first_inverse + second_inverse
    if penetration <= 0.0 or inverse_mass == 0.0:
        return

    nx, ny = (dx / distance, dy / distance) if distance > 1e-10 else (1.0, 0.0)
    shift = penetration / inverse_mass
    first.x += nx * shift * first_inverse
    first.y += ny * shift * first_inverse
    second.x -= nx * shift * second_inverse
    second.y -= ny * shift * second_inverse

    approach = (first.vx - second.vx) * nx + (first.vy - second.vy) * ny
    impulse = -1.12 * min(0.0, approach) / inverse_mass
    first.vx += nx * impulse * first_inverse
    first.vy += ny * impulse * first_inverse
    second.vx -= nx * impulse * second_inverse
    second.vy -= ny * impulse * second_inverse


def _tank_circle_intersections(body: CircleBody, radius: float, settings: Settings) -> list[tuple[float, float]]:
    left = top = settings.particle_radius
    right, bottom = settings.width - left, settings.height - top
    points = []
    for x in (left, right):
        remaining = radius * radius - (x - body.x) ** 2
        if remaining >= 0.0:
            offset = sqrt(remaining)
            points.extend((x, y) for y in (body.y - offset, body.y + offset) if top <= y <= bottom)
    for y in (top, bottom):
        remaining = radius * radius - (y - body.y) ** 2
        if remaining >= 0.0:
            offset = sqrt(remaining)
            points.extend((x, y) for x in (body.x - offset, body.x + offset) if left <= x <= right)
    return points


def collide_particle(particle: Particle, body: CircleBody, mass: float, settings: Settings) -> bool:
    dx, dy = particle.x - body.x, particle.y - body.y
    limit = body.radius + settings.particle_radius
    distance_squared = dx * dx + dy * dy
    if distance_squared >= limit * limit - 1e-10:
        return False

    distance = sqrt(distance_squared)
    nx, ny = (dx / distance, dy / distance) if distance > 1e-10 else (0.0, -1.0)
    x, y = body.x + nx * limit, body.y + ny * limit
    wall = settings.particle_radius
    if not (wall <= x <= settings.width - wall and wall <= y <= settings.height - wall):
        points = _tank_circle_intersections(body, limit, settings)
        if points:
            x, y = min(points, key=lambda point: (point[0] - particle.x) ** 2 + (point[1] - particle.y) ** 2)
            nx, ny = (x - body.x) / limit, (y - body.y) / limit
    particle.x, particle.y = x, y

    approach = (particle.vx - body.vx) * nx + (particle.vy - body.vy) * ny
    inverse_body_mass = body.inverse_mass
    impulse = -1.10 * min(0.0, approach) / (1.0 / mass + inverse_body_mass)
    particle.vx += nx * impulse / mass
    particle.vy += ny * impulse / mass
    body.vx -= nx * impulse * inverse_body_mass
    body.vy -= ny * impulse * inverse_body_mass
    return True
