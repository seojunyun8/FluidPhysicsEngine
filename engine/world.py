from dataclasses import dataclass
from math import hypot
from random import Random

from .contacts import keep_in_tank
from .particles import Particle
from .settings import Settings
from .spatial_grid import SpatialGrid
from .sph import SphSolver


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
        self.grid = SpatialGrid(settings.smoothing_radius)
        self.solver = SphSolver(settings, settings.particle_mass)
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
