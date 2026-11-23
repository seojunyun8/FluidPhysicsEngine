from math import hypot

import pygame

from engine.world import Stir
from scenes import Scene, load_scene

from .layout import BUTTONS, SIZE, TANK, fit_canvas, logical_point
from .renderer import Renderer


KEYS = {
    pygame.K_1: "dam",
    pygame.K_2: "float",
    pygame.K_SPACE: "pause",
    pygame.K_r: "reset",
    pygame.K_f: "buoyancy",
    pygame.K_TAB: "view",
    pygame.K_n: "step",
}


class Lab:
    def __init__(self, scene: Scene = Scene.DAM) -> None:
        self.screen = pygame.display.set_mode(SIZE, pygame.RESIZABLE)
        pygame.display.set_caption("Fluid Physics Lab")
        self.canvas = pygame.Surface(SIZE).convert()
        self.renderer = Renderer(self.canvas)
        self.scene = scene
        self.world = load_scene(scene)
        self.running = True
        self.paused = False
        self.pressure = False
        self.step_requests = 0
        self.accumulator = 0.0
        self.emit_remaining = 0.0
        self.brush = False
        self.emitter = False
        self.last_brush_point: tuple[int, int] | None = None

    def _activate(self, action: str) -> None:
        if action in ("dam", "float", "reset"):
            if action != "reset":
                self.scene = Scene.DAM if action == "dam" else Scene.FLOAT
            buoyancy = self.world.buoyancy
            self.world = load_scene(self.scene)
            self.world.buoyancy = buoyancy
            self.accumulator = 0.0
            self.emit_remaining = 0.0
            self.step_requests = 0
        elif action == "pause":
            self.paused = not self.paused
            self.accumulator = 0.0
        elif action == "step" and self.paused:
            self.step_requests += 1
        elif action == "buoyancy" and self.scene == Scene.FLOAT:
            self.world.buoyancy = not self.world.buoyancy
            if not self.world.buoyancy:
                for body in self.world.bodies:
                    body.buoyant_force = 0.0
        elif action in ("flow", "pressure", "view"):
            self.pressure = not self.pressure if action == "view" else action == "pressure"

    def handle(self, event: pygame.event.Event) -> None:
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            self.running = False
        elif event.type == pygame.KEYDOWN and event.key in KEYS:
            self._activate(KEYS[event.key])
        elif event.type == pygame.WINDOWFOCUSLOST:
            self.brush = self.emitter = False
            self.last_brush_point = None
        elif event.type == pygame.MOUSEBUTTONDOWN:
            point = logical_point(event.pos, fit_canvas(self.screen.get_size()))
            if event.button == 1:
                self.brush = TANK.collidepoint(point)
                self.last_brush_point = point if self.brush else None
                for action, rect in BUTTONS.items():
                    if rect.collidepoint(point):
                        self._activate(action)
                        break
            elif event.button == 3:
                self.emitter = TANK.collidepoint(point)
                self.emit_remaining = 0.0
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.brush = False
                self.last_brush_point = None
            elif event.button == 3:
                self.emitter = False

    def update(self, frame_time: float, point: tuple[int, int]) -> None:
        dt = self.world.settings.dt
        if self.paused:
            steps = self.step_requests
            self.step_requests = 0
        else:
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

    def draw(self, point: tuple[int, int], fps: float) -> None:
        self.renderer.draw(self.world, self.scene, fps, self.paused, self.pressure, point, self.brush, self.emitter)
        frame = fit_canvas(self.screen.get_size())
        if frame.size == SIZE and frame.topleft == (0, 0):
            self.screen.blit(self.canvas, (0, 0))
        else:
            self.screen.fill((22, 40, 57))
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
            self.draw(point, clock.get_fps())
