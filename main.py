import os
import sys

import sdl2.ext

from typing import Dict, Tuple, List

# FYI-PSA on GitHub
# This mostly acts a project for me to test my knowledge
# in simple animations of differential equations and of SDL2 graphics in Python


# For loading extra resources like images, from a "resources" in this folder
RESOURCES_PATH: str = "resources"
RESOURCE_FILES: List[str] = os.listdir(RESOURCES_PATH)
RESOURCES: sdl2.ext.Resources = sdl2.ext.Resources(__file__, RESOURCES_PATH)

# Initialize SDL and it's subsystems
# Check documentation for this function, lots more systems to potentitally have
sdl2.ext.init(video=True)

PROGRAM_TITLE: str = "Hello World"
PROGRAM_INITIAL_SIZE: Tuple[int, int] = (500, 500)
PROGRAM_INITIAL_POSITION: Tuple[int, int] = (
        sdl2.SDL_WINDOWPOS_CENTERED,
        sdl2.SDL_WINDOWPOS_CENTERED)

# There's a lot of configurations to this, documentation is pretty good
window = sdl2.ext.Window(
        title=PROGRAM_TITLE,
        size=PROGRAM_INITIAL_SIZE,
        position=PROGRAM_INITIAL_POSITION,
        flags=(sdl2.SDL_WINDOW_RESIZABLE | sdl2.SDL_WINDOW_INPUT_GRABBED))

window.show()

sprite_factory = sdl2.ext.SpriteFactory(sdl2.ext.SOFTWARE)
sprite_renderer = sprite_factory.create_sprite_render_system(window)
sprites: Dict = {}
for resource in RESOURCE_FILES:
    resource_name, resource_extension = os.path.splitext(resource)
    if resource_extension in ['bmp', 'png', 'jpg']:
        sprites.update(
                {resource_name:
                 sprite_factory.from_image(RESOURCES.get_path(resource))
                 })
        # Edge cases of naming multiple different types of image the same thing

# Now all images in the resources folder are sprites in the dictionary

input('')
# sys.exit(0)
