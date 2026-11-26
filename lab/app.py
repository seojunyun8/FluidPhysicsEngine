from math import hypot

import pygame

from engine.world import Stir
from scenes import create_tank

from .layout import SIZE, TANK, fit_canvas, logical_point
from .tank import draw_tank


TITLE = "Fluid Physics Lab"
DRAG_THRESHOLD = 5


class Lab:
    def __init__(self) -> None:
        self.screen = pygame.display.set_mode(SIZE, pygame.RESIZABLE)
        pygame.display.set_caption(f"{TITLE} - Press 1 or click to start")
        self.canvas = pygame.Surface(SIZE).convert()
        pygame.font.init()
        font = pygame.font.Font(None, 23)
        self.controls = font.render(
            "Click: drop a ball   |   Drag: stir   |   Right mouse: add water   |   1: restart",
            True, (175, 180, 188),
        )
        self.world = create_tank()
        self.running = True
        self.started = False
        self.accumulator = 0.0
        self.emit_remaining = 0.0
        self.brush = False
        self.emitter = False
        self.press_point: tuple[int, int] | None = None
        self.last_brush_point: tuple[int, int] | None = None

    def handle(self, event: pygame.event.Event) -> None:
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.running = False
            elif event.key in (pygame.K_1, pygame.K_KP1):
                if self.started:
                    self.world = create_tank()
                self.started = True
                self.accumulator = self.emit_remaining = 0.0
                self.brush = self.emitter = False
                self.press_point = None
                self.last_brush_point = None
                pygame.display.set_caption(TITLE)
        elif event.type == pygame.WINDOWFOCUSLOST:
            self.brush = self.emitter = False
            self.press_point = None
            self.last_brush_point = None
        elif event.type == pygame.MOUSEBUTTONDOWN:
            point = logical_point(event.pos, fit_canvas(self.screen.get_size()))
            if event.button == 1:
                self.press_point = point if TANK.collidepoint(point) else None
            elif event.button == 3:
                self.emitter = TANK.collidepoint(point)
                self.emit_remaining = 0.0
        elif event.type == pygame.MOUSEMOTION and self.press_point is not None and not self.brush:
            point = logical_point(event.pos, fit_canvas(self.screen.get_size()))
            if hypot(point[0] - self.press_point[0], point[1] - self.press_point[1]) >= DRAG_THRESHOLD:
                self.brush = True
                self.last_brush_point = self.press_point
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                point = logical_point(event.pos, fit_canvas(self.screen.get_size()))
                if (self.press_point is not None and not self.brush and TANK.collidepoint(point)
                        and hypot(point[0] - self.press_point[0], point[1] - self.press_point[1]) < DRAG_THRESHOLD):
                    scale = TANK.width / self.world.settings.width
                    self.world.drop_body((point[0] - TANK.left) / scale, (point[1] - TANK.top) / scale)
                    if not self.started:
                        self.started = True
                        pygame.display.set_caption(TITLE)
                self.press_point = None
                self.brush = False
                self.last_brush_point = None
            elif event.button == 3:
                self.emitter = False

    def update(self, frame_time: float, point: tuple[int, int]) -> None:
        if not self.started:
            return

        dt = self.world.settings.dt
        self.accumulator = min(8 * dt, self.accumulator + frame_time)
        steps = int((self.accumulator + 1e-9) / dt)
        self.accumulator = max(0.0, self.accumulator - steps * dt)

        inside = TANK.collidepoint(point)
        scale = TANK.width / self.world.settings.width
        x, y = (point[0] - TANK.left) / scale, (point[1] - TANK.top) / scale
        stir = None
        if inside and self.brush:
            previous = self.last_brush_point or point
            sample_time = max(frame_time, dt) * scale
            vx, vy = (point[0] - previous[0]) / sample_time, (point[1] - previous[1]) / sample_time
            cap = min(1.0, 13.0 / max(1e-10, hypot(vx, vy)))
            stir = Stir(x, y, vx * cap, vy * cap)
            self.last_brush_point = point
        else:
            self.last_brush_point = None

        for _ in range(steps):
            if inside and self.emitter:
                self.emit_remaining -= dt
                if self.emit_remaining <= 0.0:
                    self.world.emit(x, y)
                    self.emit_remaining += 0.058
            self.world.step(stir)

    def draw(self) -> None:
        draw_tank(self.canvas, self.world)
        self.canvas.blit(self.controls, (TANK.left, TANK.bottom + 15))
        frame = fit_canvas(self.screen.get_size())
        if self.screen.get_size() == SIZE:
            self.screen.blit(self.canvas, (0, 0))
        else:
            self.screen.fill((0, 0, 0))
            self.screen.blit(pygame.transform.smoothscale(self.canvas, frame.size), frame)
        pygame.display.flip()

    def run(self) -> None:
        clock = pygame.time.Clock()
        while self.running:
            frame_time = clock.tick(60) / 1000.0
            for event in pygame.event.get():
                self.handle(event)
            if not self.running:
                break
            point = logical_point(pygame.mouse.get_pos(), fit_canvas(self.screen.get_size()))
            self.update(frame_time, point)
            self.draw()
