from itertools import combinations, product
from math import floor
from typing import Iterator

from .particles import Particle


class SpatialGrid:
    # Include each adjacent cell pair in one direction only.
    FORWARD_OFFSETS = ((1, -1), (1, 0), (1, 1), (0, 1))

    def __init__(self, cell_size: float) -> None:
        self.cell_size = cell_size
        self._cells: dict[tuple[int, int], list[Particle]] = {}

    def rebuild(self, particles: list[Particle]) -> None:
        self._cells.clear()
        scale = 1.0 / self.cell_size
        for particle in particles:
            key = (floor(particle.x * scale), floor(particle.y * scale))
            self._cells.setdefault(key, []).append(particle)

    def candidate_pairs(self) -> Iterator[tuple[Particle, Particle]]:
        for (x, y), cell in self._cells.items():
            yield from combinations(cell, 2)
            for dx, dy in self.FORWARD_OFFSETS:
                adjacent = self._cells.get((x + dx, y + dy))
                if adjacent:
                    yield from product(cell, adjacent)

    def nearby(self, x: float, y: float, radius: float) -> Iterator[Particle]:
        size = self.cell_size
        for cx in range(floor((x - radius) / size), floor((x + radius) / size) + 1):
            for cy in range(floor((y - radius) / size), floor((y + radius) / size) + 1):
                yield from self._cells.get((cx, cy), ())
