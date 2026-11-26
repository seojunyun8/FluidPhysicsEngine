from .particles import Particle
from .settings import Settings


def keep_in_tank(particle: Particle, settings: Settings) -> None:
    radius = settings.particle_radius
    right = settings.width - radius
    bottom = settings.height - radius
    bounce = 0.22

    if particle.x < radius:
        particle.x = radius
        particle.vx = max(0.0, -bounce * particle.vx)
    elif particle.x > right:
        particle.x = right
        particle.vx = min(0.0, -bounce * particle.vx)

    if particle.y < radius:
        particle.y = radius
        particle.vy = max(0.0, -bounce * particle.vy)
    elif particle.y > bottom:
        particle.y = bottom
        particle.vy = min(0.0, -bounce * particle.vy)
