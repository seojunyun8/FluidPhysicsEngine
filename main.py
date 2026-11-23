import argparse

import pygame

from lab.app import Lab
from scenes import Scene


def main() -> None:
    parser = argparse.ArgumentParser(description="Interactive 2D SPH simulator")
    parser.add_argument("--scene", choices=("dam", "buoyancy"), default="dam")
    args = parser.parse_args()
    scene = Scene.DAM if args.scene == "dam" else Scene.FLOAT
    pygame.display.init()
    pygame.font.init()
    try:
        Lab(scene).run()
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()
