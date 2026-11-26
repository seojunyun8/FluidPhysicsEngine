from dataclasses import dataclass
from itertools import combinations
from math import hypot
from random import Random

from .contacts import collide_with_circle, keep_in_tank
from .particles import Particle
from .rigid import CircleBody
from .settings import Settings
from .spatial_grid import SpatialGrid
from .sph import SphSolver


MAX_BODIES = 12


@dataclass(frozen=True, slots=True)
class Stir:
    x: float
    y: float
    vx: float
    vy: float


class World:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.particles: list[Particle] = []
        self.bodies: list[CircleBody] = []
        particle_mass = settings.particle_mass
        self.grid = SpatialGrid(settings.smoothing_radius)
        self.solver = SphSolver(settings, particle_mass)
        self.particle_inverse_mass = 1.0 / particle_mass
        self.random = Random(29)

    def seed_block(self, left: float, top: float, columns: int, rows: int) -> None:
        for row in range(rows):
            for column in range(columns):
                x = left + column * self.settings.spacing + self.random.uniform(-0.012, 0.012)
                y = top + row * self.settings.spacing + self.random.uniform(-0.012, 0.012)
                self._add_particle(x, y)

    def emit(self, x: float, y: float) -> None:
        spread = self.settings.spacing * 0.55
        for dx in (-spread, spread):
            self._add_particle(x + dx, y + self.random.uniform(-spread, spread), dx * 3.0, 1.0)

    def drop_body(self, x: float, y: float) -> None:
        if len(self.bodies) >= MAX_BODIES:
            return
        body = CircleBody(x, y)
        keep_in_tank(body, self.settings, radius=body.radius)
        if any(hypot(body.x - other.x, body.y - other.y) < body.radius + other.radius for other in self.bodies):
            return
        self.bodies.append(body)

    def _add_particle(self, x: float, y: float, vx: float = 0.0, vy: float = 0.0) -> None:
        settings = self.settings
        radius = settings.particle_radius
        if (len(self.particles) >= settings.max_particles
                or not (radius <= x <= settings.width - radius and radius <= y <= settings.height - radius)):
            return
        self.particles.append(Particle(x, y, vx, vy))

    def _stir(self, stir: Stir) -> None:
        radius = 0.85
        for particle in self.grid.nearby(stir.x, stir.y, radius):
            distance = hypot(particle.x - stir.x, particle.y - stir.y)
            if distance < radius:
                strength = 24.0 * (1.0 - distance / radius)
                particle.ax += (stir.vx - particle.vx) * strength
                particle.ay += (stir.vy - particle.vy) * strength

    def measure_fluid(self) -> None:
        self.grid.rebuild(self.particles)
        self.solver.evaluate(self.particles, self.grid)

    def step(self, stir: Stir | None = None) -> None:
        settings = self.settings
        dt = settings.dt
        self.measure_fluid()
        if stir is not None:
            self._stir(stir)

        for particle in self.particles:
            particle.vx += particle.ax * dt
            particle.vy += particle.ay * dt
            particle.x += particle.vx * dt
            particle.y += particle.vy * dt
            keep_in_tank(particle, settings)

        for body in self.bodies:
            body.vy += settings.gravity * dt
            body.x += body.vx * dt
            body.y += body.vy * dt
            keep_in_tank(body, settings, radius=body.radius)
        if self.bodies:
            self._resolve_body_contacts()

    def _resolve_body_contacts(self) -> None:
        settings = self.settings
        for _ in range(2):
            for first, second in combinations(self.bodies, 2):
                collide_with_circle(first, second, first.radius + second.radius, first.inverse_mass)
            self.grid.rebuild(self.particles)
            for body in self.bodies:
                keep_in_tank(body, settings, radius=body.radius)
                limit = body.radius + settings.particle_radius
                for particle in self.grid.nearby(body.x, body.y, limit):
                    if collide_with_circle(particle, body, limit, self.particle_inverse_mass):
                        keep_in_tank(particle, settings)
                keep_in_tank(body, settings, radius=body.radius)
