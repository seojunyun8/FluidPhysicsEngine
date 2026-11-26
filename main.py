import pygame

from lab.app import Lab


def main() -> None:
    pygame.display.init()
    try:
        Lab().run()
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()
