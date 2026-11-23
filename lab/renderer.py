import pygame

from engine.rigid import CircleBody
from engine.world import World
from scenes import Scene

from .layout import BUTTONS, PANEL, TANK
from .tank import Tank


INK = (22, 40, 57)
MUTED = (72, 96, 113)
LINE = (211, 223, 231)
WHITE = (252, 254, 255)
TEAL = (8, 107, 126)


class Renderer:
    def __init__(self, canvas: pygame.Surface) -> None:
        self.canvas = canvas
        self.title = pygame.font.SysFont("segoeui,arial", 37, bold=True)
        self.heading = pygame.font.SysFont("segoeui,arial", 23, bold=True)
        self.body = pygame.font.SysFont("segoeui,arial", 16)
        self.button = pygame.font.SysFont("segoeui,arial", 15, bold=True)
        self.small = pygame.font.SysFont("segoeui,arial", 14)
        self.mono = pygame.font.SysFont("consolas,couriernew", 15)
        self.tank = Tank(self.mono)

    def _text(
        self, value: str, x: int, y: int, font: pygame.font.Font, color: tuple[int, int, int] = INK,
        align_right: bool = False,
    ) -> None:
        image = font.render(value, True, color)
        self.canvas.blit(image, (x - image.get_width() if align_right else x, y))

    def _button(self, key: str, label: str, pointer: tuple[int, int], selected: bool = False) -> None:
        rect = BUTTONS[key]
        hover = rect.collidepoint(pointer)
        fill = (9, 94, 115) if selected else ((230, 243, 248) if hover else WHITE)
        pygame.draw.rect(self.canvas, fill, rect, border_radius=8)
        pygame.draw.rect(self.canvas, fill if selected else LINE, rect, 1, border_radius=8)
        image = self.button.render(label, True, WHITE if selected else INK)
        self.canvas.blit(image, image.get_rect(center=rect.center))

    def draw(
        self, world: World, scene: Scene, fps: float, paused: bool, pressure: bool, pointer: tuple[int, int],
        brush: bool, emitter: bool,
    ) -> None:
        self.canvas.fill((237, 243, 247))
        pygame.draw.circle(self.canvas, TEAL, (51, 49), 23)
        for start_y in (42, 49, 56):
            pygame.draw.lines(self.canvas, (229, 251, 251), False,
                              [(39, start_y), (45, start_y - 2), (52, start_y + 1), (62, start_y - 1)], 2)
        self._text("Fluid Physics Lab", 88, 18, self.title)
        self._text("2D particle simulation  /  Smoothed Particle Hydrodynamics", 91, 61, self.small, MUTED)
        pygame.draw.circle(self.canvas, (203, 134, 61) if paused else (24, 145, 113), (824, 51), 4)
        self._text("Paused" if paused else "Running", 836, 41, self.body, MUTED)
        self._button("pause", "Resume" if paused else "Pause", pointer)
        self._button("reset", "Reset", pointer)

        self._button("dam", "1   Dam Break", pointer, scene == Scene.DAM)
        self._button("float", "2   Buoyancy", pointer, scene == Scene.FLOAT)
        time = world.steps * world.settings.dt
        self._text(f"{time:06.2f} s    {fps:02.0f} FPS", TANK.right, 105, self.mono, MUTED, align_right=True)
        self.tank.draw(self.canvas, world, pressure, pointer, brush, emitter)
        self._draw_panel(world, scene, pressure, pointer)
        self._text("Drag to stir   /   Hold right mouse to add water", 28, 664, self.body)
        self._text("Space  pause / resume     N  step     R  reset     Tab  view     F  buoyancy", 28, 692, self.small, MUTED)
        pygame.draw.line(self.canvas, LINE, (28, 732), (1172, 732))
        self._text("TANK  12.0 × 7.2 m", 28, 741, self.mono, MUTED)
        self._text(f"FIXED STEP  {world.settings.dt * 1000:g} ms", 1172, 741, self.mono, MUTED, align_right=True)

    def _draw_panel(self, world: World, scene: Scene, pressure: bool, pointer: tuple[int, int]) -> None:
        pygame.draw.rect(self.canvas, WHITE, PANEL, border_radius=12)
        pygame.draw.rect(self.canvas, LINE, PANEL, 1, border_radius=12)
        self._text("Diagnostics", 909, 110, self.heading)
        self._text("Particle solver", 909, 143, self.small, MUTED)
        count = len(world.particles)
        total_pairs = count * (count - 1) // 2
        metrics = world.metrics
        ratio = 100.0 * metrics.candidates / max(1, total_pairs)
        density = world.settings.rest_density
        rows = (
            ("Particles", f"{count:,}"),
            ("SPH neighbor pairs", f"{metrics.neighbors:,}"),
            ("Grid / all-pairs checks", f"{ratio:.1f}%"),
            ("Mean density / target", f"{metrics.mean_density / density:.2f}×"),
            ("Peak density / target", f"{metrics.peak_density / density:.2f}×"),
        )
        for index, (label, value) in enumerate(rows):
            y = 177 + index * 31
            self._text(label, 909, y, self.body, MUTED)
            self._text(value, 1153, y + 2, self.mono, INK, align_right=True)
        pygame.draw.line(self.canvas, LINE, (909, 335), (1153, 335))
        self._text("Particle color", 909, 355, self.body)
        self._button("flow", "Speed", pointer, not pressure)
        self._button("pressure", "Pressure", pointer, pressure)
        pygame.draw.circle(self.canvas, (43, 134, 224) if pressure else (24, 170, 205), (914, 437), 4)
        self._text("Low", 924, 429, self.small, MUTED)
        pygame.draw.circle(self.canvas, (255, 196, 102) if pressure else (164, 248, 235), (1109, 437), 4)
        self._text("High", 1120, 429, self.small, MUTED)
        if scene == Scene.FLOAT:
            label = "Buoyancy  ON" if world.buoyancy else "Buoyancy  OFF"
            self._button("buoyancy", label, pointer, world.buoyancy)
            for index, body in enumerate(world.bodies):
                self._body_card(body, world.settings.rest_density, 528 + index * 81)
        else:
            pygame.draw.line(self.canvas, LINE, (909, 469), (1153, 469))
            self._text("Dam break", 909, 484, self.heading)
            self._text("Watch the released water spread", 909, 525, self.body, MUTED)
            self._text("around two fixed circular piers.", 909, 548, self.body, MUTED)
            self._text("Switch to Pressure to inspect", 909, 582, self.body, MUTED)
            self._text("compression at impact.", 909, 605, self.body, MUTED)

    def _body_card(self, body: CircleBody, density: float, y: int) -> None:
        accent = (224, 156, 72) if body.name == "Light" else (163, 111, 200)
        pygame.draw.rect(self.canvas, (242, 246, 249), (909, y, 244, 72), border_radius=8)
        pygame.draw.circle(self.canvas, accent, (924, y + 16), 4)
        self._text(body.name, 935, y + 6, self.button)
        self._text(f"{body.density / density:.2f}× water", 1143, y + 8, self.mono, MUTED, align_right=True)
        self._text(f"{body.submerged:.0%} submerged", 920, y + 29, self.small, MUTED)
        self._text(f"{body.buoyant_force:.1f} N up", 1143, y + 31, self.mono, MUTED, align_right=True)
        pygame.draw.rect(self.canvas, LINE, (920, y + 56, 222, 5), border_radius=3)
        if body.submerged > 0.0:
            pygame.draw.rect(self.canvas, accent, (920, y + 56, max(1, round(222 * body.submerged)), 5), border_radius=3)
