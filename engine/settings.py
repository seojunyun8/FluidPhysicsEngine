from dataclasses import dataclass
from math import ceil, pi


@dataclass(frozen=True, slots=True)
class Settings:
    width: float = 12.0
    height: float = 7.2
    spacing: float = 0.18
    particle_radius: float = 0.063
    smoothing_radius: float = 0.35
    rest_density: float = 1.0
    stiffness: float = 78.0
    viscosity: float = 0.065
    gravity: float = 9.81
    dt: float = 1.0 / 120.0
    max_particles: int = 1100

    @property
    def particle_mass(self) -> float:
        # A regular interior patch should start at the reference density.
        h = self.smoothing_radius
        reach = ceil(h / self.spacing)
        weight = 0.0
        for x in range(-reach, reach + 1):
            for y in range(-reach, reach + 1):
                r_squared = (x * x + y * y) * self.spacing ** 2
                weight += max(0.0, h * h - r_squared) ** 3
        return self.rest_density / (4.0 / (pi * h ** 8) * weight)
