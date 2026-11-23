from dataclasses import dataclass
from math import pi, sqrt

from .particles import Particle
from .settings import Settings
from .spatial_grid import SpatialGrid


@dataclass(frozen=True, slots=True)
class FluidMetrics:
    candidates: int = 0
    neighbors: int = 0
    mean_density: float = 0.0
    peak_density: float = 0.0


class SphSolver:
    def __init__(self, settings: Settings, mass: float) -> None:
        self.settings = settings
        self.h = settings.smoothing_radius
        self.h_squared = self.h * self.h
        self.density_weight = mass * 4.0 / (pi * self.h ** 8)
        self.self_density = self.density_weight * self.h_squared ** 3
        self.pressure_weight = mass * 30.0 / (pi * self.h ** 5)

    def evaluate(self, particles: list[Particle], grid: SpatialGrid) -> FluidMetrics:
        """Compute density first, then use each neighbor pair once for both forces."""
        settings = self.settings
        for particle in particles:
            particle.density = self.self_density
            particle.ax = 0.0
            particle.ay = settings.gravity

        neighbors = []
        candidates = 0
        for first, second in grid.candidate_pairs():
            candidates += 1
            dx = first.x - second.x
            dy = first.y - second.y
            distance_squared = dx * dx + dy * dy
            remaining = self.h_squared - distance_squared
            if remaining > 0.0:
                density = self.density_weight * remaining * remaining * remaining
                first.density += density
                second.density += density
                neighbors.append((first, second, dx, dy, distance_squared))

        total_density = 0.0
        peak_density = 0.0
        for particle in particles:
            density = particle.density
            pressure = max(0.0, settings.stiffness * (density - settings.rest_density))
            particle.pressure = pressure
            particle.inverse_density = 1.0 / density
            particle.pressure_factor = pressure * particle.inverse_density ** 2
            total_density += density
            peak_density = max(peak_density, density)

        regularization = 0.01 * self.h_squared
        for first, second, dx, dy, distance_squared in neighbors:
            distance = sqrt(distance_squared)
            gap = self.h - distance
            gradient = self.pressure_weight * gap * gap
            # Coincident particles still exchange viscosity. Use a deterministic
            # direction for their pressure so they can separate.
            nx, ny = (dx / distance, dy / distance) if distance > 1e-10 else (1.0, 0.0)
            pressure = gradient * (first.pressure_factor + second.pressure_factor)
            viscosity = (
                settings.viscosity * (first.inverse_density + second.inverse_density)
                * gradient * (distance + 0.05 * self.h) / (distance_squared + regularization)
            )
            ax = pressure * nx + viscosity * (second.vx - first.vx)
            ay = pressure * ny + viscosity * (second.vy - first.vy)
            first.ax += ax
            first.ay += ay
            second.ax -= ax
            second.ay -= ay

        return FluidMetrics(candidates, len(neighbors), total_density / max(1, len(particles)), peak_density)
