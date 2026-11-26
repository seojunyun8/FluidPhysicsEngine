from engine.settings import Settings
from engine.world import World


def create_tank() -> World:
    world = World(Settings())
    world.seed_block(0.18, 0.72, 22, 32)
    world.seed_block(4.20, 6.72, 43, 2)
    world.measure_fluid()
    return world
