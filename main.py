#!/bin/python3.10

import sys
import time
import threading
import numpy as np

import sdl2
import sdl2.ext

from typing import List, Tuple, Dict, Callable


# FYI-PSA on GitHub
# This mostly acts a project for me to test my knowledge
# in simple animations of differential equations and of SDL2 graphics in Python


class Pendulum():
    def __init__(self,
                 length: float = 1,
                 initial_angle: float = (np.pi/3),
                 initial_angular_velocity: float = 0,
                 mass_kg: float = 0.2,
                 radius: float = 1.0,
                 gravity: float = 9.8) -> None:
        self.length: float = length
        self.radius: float = radius
        self.mass: float = mass_kg
        self.volume: float = np.power(radius, 3) * np.pi * 4 / 3
        self.face_area: float = np.power(radius, 2) * np.pi
        self.density: float = mass_kg / self.volume
        self.gravity: float = gravity
        self.mass_length: float = mass_kg * length
        self.omega_squared: float = gravity / length
        self.angle: float = initial_angle
        self.angular_velocity: float = initial_angular_velocity
        self.air_density = 1.225
        self.air_dynamic_viscosity = 0.00001813

    def get_position(self) -> Tuple[float, float]:
        y: float = self.length * np.cos(self.angle)
        x: float = self.length * np.sin(self.angle)
        return (x, y)

    def get_properties(self) -> Dict[str, float]:
        return {'mass': self.mass,
                'radius': self.radius,
                'length': self.length}

    def reynold_number(self) -> float:
        # wind: float = 0.2
        wind: float = 0.0000001
        return np.abs((wind + np.abs(self.angular_velocity * self.length))
                      * (self.radius)
                      * (self.air_density)
                      / (self.air_dynamic_viscosity))

    def drag_coefficient(self) -> float:
        # You may remove the following comment if you just want a constant
        # return 0.47
        reynolds: float = self.reynold_number()
        if reynolds == 0:
            return 1e+306
        if reynolds < 1:
            return (24 / reynolds)
        elif reynolds <= 3e+5:
            return (0.47)
        else:
            # I couldn't get the approximation
            # for the function for ~0.47 to ~0.3 to work properly, so:
            return (0.3)

    def drag_force(self) -> float:
        velocity = self.length * self.angular_velocity
        force = (0.5
                 * self.drag_coefficient()
                 * self.air_density
                 * self.face_area
                 * velocity)
        # You may remove these comment for the drag force to be simple
        # modifier = 0.5
        # return (velocity * modifier)
        return force

    def move_dt(self, dt: float = 0.05) -> None:
        angular_acceleration: float = self.omega_squared * np.sin(self.angle)
        angular_acceleration += (self.drag_force() / self.mass_length)
        angular_acceleration = -angular_acceleration
        self.angle += self.angular_velocity * dt
        self.angular_velocity += angular_acceleration * dt


class SDLGraphics():
    def __init__(self,
                 title: str = "Pendulum Simulation",
                 fullscreen: bool = True,
                 time_scale: float = 1.0,
                 size_scale: float = 35) -> None:

        # Initialize SDL and it's subsystems
        # In general this module has good-enough documentation worth reading
        sdl2.ext.init(video=True)

        window_initial_size: Tuple[int, int] = (600, 600)
        window_initial_position: Tuple[int, int] = (
                sdl2.SDL_WINDOWPOS_CENTERED,
                sdl2.SDL_WINDOWPOS_CENTERED)

        # There's a lot of configurations to this, docs
        flags = sdl2.SDL_WINDOW_RESIZABLE
        if fullscreen:
            flags = flags | sdl2.SDL_WINDOW_FULLSCREEN_DESKTOP
        self.MAIN_WINDOW: sdl2.ext.Window = sdl2.ext.Window(
                title=title,
                size=window_initial_size,
                position=window_initial_position,
                flags=flags)

        self.MAIN_WINDOW.show()

        # NOTE:
        # Can define a logical size to this that scales with the actual window
        # it'll supposedly get automatically scaled to be more performant
        # Don't really need it right now
        self.RENDERER: sdl2.ext.Renderer = sdl2.ext.Renderer(
                self.MAIN_WINDOW,
                flags=(sdl2.SDL_RENDERER_TARGETTEXTURE | 0)
                )

        self.BG_COLOR: sdl2.ext.Color = sdl2.ext.color.string_to_color(
                '0x0D0D0D')
        self.OBJ_COLOR: sdl2.ext.Color = sdl2.ext.color.string_to_color(
                '0x20B0D3')
        self.ARM_COLOR: sdl2.ext.Color = sdl2.ext.color.string_to_color(
                '0xEC6B6B')

        self.SCALING_FACTOR = size_scale
        self.TIME_SCALE = time_scale
        # self.SCALING_FACTOR: float = 35
        # self.TIME_SCALE: float = 5.0
        # self.TIME_SCALE: float = 0.5
        # self.TIME_SCALE: float = 1.0

    def draw_centered_rectangle(self,
                                renderer: sdl2.ext.Renderer,
                                center: Tuple[float, float],
                                size: Tuple[float, float],
                                color: sdl2.ext.Color) -> None:
        offset = (size[0] / 2, size[1] / 2)
        position = (center[0] - offset[0], center[1] - offset[1])
        renderer.fill(color=color,
                      rects=(position[0], position[1],
                             size[0], size[1]))

    def draw_centered_circle_approximate(self,
                                         renderer: sdl2.ext.Renderer,
                                         center: Tuple[float, float],
                                         radius: float,
                                         color: sdl2.ext.Color) -> None:
        side = radius * np.sqrt(2)
        self.draw_centered_rectangle(renderer, center, (side, side), color)
        width = radius * np.sqrt(14)/2
        height = radius * np.sqrt(2)/2
        self.draw_centered_rectangle(renderer,
                                     (center[0], center[1]),
                                     (height, width),
                                     color)
        self.draw_centered_rectangle(renderer,
                                     (center[0], center[1]),
                                     (width, height),
                                     color)

    def draw_thick_line(self,
                        renderer: sdl2.ext.Renderer,
                        start: Tuple[float, float],
                        end: Tuple[float, float],
                        width: float,
                        color: sdl2.ext.Color) -> None:
        if end == start:
            return

        extra_length: float = (width * 10)

        horizontal_dist: float = end[0] - start[0]
        vertical_dist: float = end[1] - start[1]
        hyp: float = np.sqrt(np.power(vertical_dist, 2)
                             + np.power(horizontal_dist, 2))
        x_coeff: float = 0.5 * (vertical_dist / hyp)
        y_coeff: float = -0.5 * (horizontal_dist / hyp)

        points: List[Tuple[float, float]] = [
                (start[0] - extra_length * x_coeff,
                 start[1] - extra_length * y_coeff),

                (end[0] - extra_length * x_coeff,
                 end[1] - extra_length * y_coeff),

                (end[0] + extra_length * x_coeff,
                 end[1] + extra_length * y_coeff),

                (start[0] + extra_length * x_coeff,
                 start[1] + extra_length * y_coeff),

                (start[0] - extra_length * x_coeff,
                 start[1] - extra_length * y_coeff)
                ]
        renderer.draw_line(color=color, points=points)

    def graphical_mainloop(self,
                           relative_position_getter: Callable,
                           object_properties_getter: Callable) -> None:
        continue_execution: bool = True
        self.RENDERER.clear(color=self.BG_COLOR)
        self.RENDERER.present()
        self.MAIN_WINDOW.refresh()

        radius: float = object_properties_getter()[
                'radius'] * self.SCALING_FACTOR

        while continue_execution:
            events: List[sdl2.SDL_Event] = sdl2.ext.get_events()
            for event in events:
                if event.type == sdl2.SDL_QUIT:
                    continue_execution = False
                    break
            center: Tuple[float, float] = (self.RENDERER.logical_size[0] / 2,
                                           self.RENDERER.logical_size[1] / 2)
            offset: Tuple[float, float] = relative_position_getter()
            position = (center[0] + offset[0] * self.SCALING_FACTOR,
                        center[1] + offset[1] * self.SCALING_FACTOR)
            self.RENDERER.clear(color=self.BG_COLOR)
            self.draw_thick_line(renderer=self.RENDERER,
                                 color=self.ARM_COLOR,
                                 width=1.75,
                                 start=(position[0], position[1]),
                                 end=(center[0], center[1]))
            self.draw_centered_circle_approximate(renderer=self.RENDERER,
                                                  color=self.OBJ_COLOR,
                                                  center=position,
                                                  radius=radius)
            self.RENDERER.present()
            self.MAIN_WINDOW.refresh()


def pendulum_thread(pendulum: Pendulum, finish: threading.Event,
                    framerate: None | int = None,
                    time_scale: float = 1.0) -> None:
    if framerate is None or framerate == 0:
        dt: float = 0.0000001
    else:
        dt: float = (1 / framerate)
    last_time: float = time.time() - dt
    while (not finish.is_set()):
        if (Dt := ((current_time := time.time()) - last_time)) >= dt:
            pendulum.move_dt(Dt * time_scale)
            last_time = current_time


def main(_: List[str]) -> int:
    pendulum = Pendulum(length=11,
                        radius=1.25,
                        initial_angle=np.pi/2,
                        initial_angular_velocity=0,
                        mass_kg=4.0,
                        gravity=np.power(np.pi, 2))
    execution_end: threading.Event = threading.Event()
    graphics = SDLGraphics(time_scale=1.0, size_scale=33)
    physics_thread: threading.Thread = threading.Thread(
            target=pendulum_thread,
            args=(pendulum, execution_end, None, graphics.TIME_SCALE)
            )
    try:
        time.sleep(2)
        physics_thread.start()
        graphics.graphical_mainloop(pendulum.get_position,
                                    pendulum.get_properties)
    except KeyboardInterrupt:
        pass
    finally:
        execution_end.set()
    if physics_thread.is_alive():
        physics_thread.join(timeout=5)
    if physics_thread.is_alive():
        print('WARNING: Physics thread failed to terminate normally.')
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
