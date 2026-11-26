from dataclasses import dataclass


@dataclass(slots=True)
class Particle:
    x: float
    y: float
    vx: float = 0.0
    vy: float = 0.0
    density: float = 0.0
    ax: float = 0.0
    ay: float = 0.0
    pressure_factor: float = 0.0
    inverse_density: float = 0.0
