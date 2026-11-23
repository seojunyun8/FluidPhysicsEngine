from dataclasses import dataclass
from math import pi


@dataclass(slots=True)
class CircleBody:
    name: str
    x: float
    y: float
    radius: float
    density: float
    fixed: bool = False
    vx: float = 0.0
    vy: float = 0.0
    submerged: float = 0.0
    buoyant_force: float = 0.0
    surface_y: float | None = None

    @property
    def area(self) -> float:
        return pi * self.radius ** 2

    @property
    def inverse_mass(self) -> float:
        return 0.0 if self.fixed else 1.0 / (self.density * self.area)
