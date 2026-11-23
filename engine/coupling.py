from math import acos, pi, sqrt

from .particles import Particle
from .rigid import CircleBody
from .settings import Settings
from .spatial_grid import SpatialGrid


def submerged_fraction(center_y: float, radius: float, surface_y: float) -> float:
    """Fraction of a disk below the horizontal waterline, with y pointing down."""
    offset = (surface_y - center_y) / radius
    if offset <= -1.0:
        return 1.0
    if offset >= 1.0:
        return 0.0
    return (acos(offset) - offset * sqrt(1.0 - offset * offset)) / pi


def _estimate_surface(body: CircleBody, nearby: list[Particle], settings: Settings) -> float | None:
    # Use fluid beside the disk, where particles are not displaced by its volume.
    # The second-highest dense particle rejects a lone droplet above the pool.
    left, right = [], []
    edge = body.radius + settings.smoothing_radius
    for particle in nearby:
        dx = particle.x - body.x
        if body.radius <= abs(dx) <= edge and particle.density >= settings.rest_density * 0.56:
            (left if dx < 0.0 else right).append(particle.y)
    heights = [sorted(side)[1] for side in (left, right) if len(side) >= 2]
    if not heights:
        return None
    return sum(heights) / len(heights) - settings.spacing * 0.42


def exchange_forces(
    body: CircleBody, grid: SpatialGrid, settings: Settings, particle_mass: float, buoyancy: bool
) -> tuple[float, float]:
    reach = body.radius + 1.7 * settings.smoothing_radius
    nearby = [particle for particle in grid.nearby(body.x, body.y, reach) if abs(particle.y - body.y) <= reach]
    surface_y = _estimate_surface(body, nearby, settings)
    body.surface_y = surface_y
    body.submerged = 0.0 if surface_y is None else submerged_fraction(body.y, body.radius, surface_y)
    body.buoyant_force = 0.0
    if body.submerged == 0.0 or surface_y is None:
        return 0.0, 0.0

    support = []
    weight_sum = flow_x = flow_y = 0.0
    for particle in nearby:
        if particle.y < surface_y:
            continue
        distance_squared = (particle.x - body.x) ** 2 + (particle.y - body.y) ** 2
        weight = 1.0 - distance_squared / (reach * reach)
        if weight <= 0.0:
            continue
        support.append((particle, weight))
        weight_sum += weight
        flow_x += particle.vx * weight
        flow_y += particle.vy * weight
    if weight_sum == 0.0:
        return 0.0, 0.0

    wetted_area = body.area * body.submerged
    if buoyancy:
        body.buoyant_force = settings.rest_density * settings.gravity * wetted_area
    drag = 7.0 * wetted_area * settings.rest_density
    force_x = drag * (flow_x / weight_sum - body.vx)
    force_y = drag * (flow_y / weight_sum - body.vy) - body.buoyant_force

    # The distributed reaction and the force on the body sum to zero.
    reaction_scale = 1.0 / (particle_mass * weight_sum)
    for particle, weight in support:
        particle.ax -= force_x * weight * reaction_scale
        particle.ay -= force_y * weight * reaction_scale
    return force_x, force_y
