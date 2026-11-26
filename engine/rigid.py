from dataclasses import dataclass


@dataclass(slots=True)
class CircleBody:
    x: float
    y: float
    radius: float = 0.42
    mass: float = 1.5
    vx: float = 0.0
    vy: float = 0.0

    @property
    def inverse_mass(self) -> float:
        return 1.0 / self.mass
