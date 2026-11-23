from dataclasses import dataclass
from itertools import combinations
from math import hypot
from random import Random

from .contacts import collide_particle, keep_in_tank, separate_bodies
from .coupling import exchange_forces
from .particles import Particle
from .rigid import CircleBody
from .settings import Settings
from .spatial_grid import SpatialGrid
from .sph import FluidMetrics, SphSolver


@dataclass(frozen=True, slots=True)
class Stir:
    x: float
    y: float
    vx: float
    vy: float


class World:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.mass = settings.particle_mass
        self.particles: list[Particle] = []
        self.bodies: list[CircleBody] = []
        self.grid = SpatialGrid(settings.smoothing_radius)
        self.solver = SphSolver(settings, self.mass)
        self.metrics = FluidMetrics()
        self.buoyancy = True
        self.steps = 0
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

    def _add_particle(self, x: float, y: float, vx: float = 0.0, vy: float = 0.0) -> None:
        settings = self.settings
        radius = settings.particle_radius
        if (len(self.particles) >= settings.max_particles
                or not (radius <= x <= settings.width - radius and radius <= y <= settings.height - radius)):
            return
        if any(hypot(x - body.x, y - body.y) < body.radius + radius for body in self.bodies):
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
        self.metrics = self.solver.evaluate(self.particles, self.grid)

    def step(self, stir: Stir | None = None) -> None:
        settings = self.settings
        dt = settings.dt
        self.measure_fluid()
        if stir is not None:
            self._stir(stir)

        moving_bodies = [body for body in self.bodies if not body.fixed]
        for body in moving_bodies:
            fx, fy = exchange_forces(body, self.grid, settings, self.mass, self.buoyancy)
            inverse_mass = body.inverse_mass
            body.vx += fx * inverse_mass * dt
            body.vy += (fy * inverse_mass + settings.gravity) * dt
            body.x += body.vx * dt
            body.y += body.vy * dt
            keep_in_tank(body, body.radius, settings, 0.14)

        for first, second in combinations(self.bodies, 2):
            separate_bodies(first, second)
        for body in moving_bodies:
            keep_in_tank(body, body.radius, settings, 0.14)

        for particle in self.particles:
            particle.vx += particle.ax * dt
            particle.vy += particle.ay * dt
            particle.x += particle.vx * dt
            particle.y += particle.vy * dt
            keep_in_tank(particle, settings.particle_radius, settings, 0.22)
            for _ in range(3):
                contacted = False
                for body in self.bodies:
                    contacted |= collide_particle(particle, body, self.mass, settings)
                if not contacted:
                    break
                keep_in_tank(particle, settings.particle_radius, settings, 0.22)
        self.steps += 1
