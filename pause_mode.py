import os
from pathlib import Path

from pico2d import *
import game_framework
import game_world


def init():
    global font
    font_path = Path(os.environ.get('WINDIR', 'C:/Windows')) / 'Fonts' / 'consola.ttf'
    font = load_font(str(font_path), 64)


def finish():
    global font
    del font


def handle_events():
    for event in get_events():
        if event.type == SDL_QUIT:
            game_framework.quit()
            return
        elif event.type == SDL_KEYDOWN and event.key == SDLK_p:
            game_framework.pop_mode()
            return


def update():
    # Keep all game objects frozen until P is pressed again.
    pass


def render():
    clear_canvas()
    game_world.render()
    x, y = get_canvas_width() // 2, get_canvas_height() // 2
    draw_rectangle(x - 160, y - 50, x + 160, y + 50,
                   0, 0, 0, 255, filled=True)
    font.draw(x - 105, y, 'PAUSED', (255, 255, 255))
    update_canvas()
