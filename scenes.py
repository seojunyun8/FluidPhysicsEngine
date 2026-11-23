from enum import IntEnum

from engine.rigid import CircleBody
from engine.settings import Settings
from engine.world import World


class Scene(IntEnum):
    DAM = 1
    FLOAT = 2


def load_scene(scene: Scene) -> World:
    settings = Settings()
    world = World(settings)
    if scene == Scene.DAM:
        world.bodies.extend((
            CircleBody("Pier A", 6.15, 5.95, 0.91, 1.0, fixed=True),
            CircleBody("Pier B", 9.0, 5.15, 0.59, 1.0, fixed=True),
        ))
        world.seed_block(0.25, 1.56, 13, 19)
    else:
        world.bodies.extend((
            CircleBody("Light", 3.45, 2.55, 0.68, 0.55),
            CircleBody("Heavy", 8.55, 2.55, 0.68, 1.70),
        ))
        world.seed_block(0.29, 4.38, 39, 9)
    world.measure_fluid()
    return world
