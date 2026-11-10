from pathlib import Path

from pico2d import *
import game_framework
import play_mode


def init():
    global image
    image = load_image(str(Path(__file__).with_name('item_select.png')))


def finish():
    global image
    del image


def handle_events():
    for event in get_events():
        if event.type == SDL_QUIT:
            game_framework.quit()
            return
        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_i:
                game_framework.pop_mode()
                return
            elif event.key in (SDLK_0, SDLK_1, SDLK_2):
                play_mode.boy.item = event.key - SDLK_0


def update():
    # 아이템 선택 중에는 플레이 월드를 갱신하지 않는다.
    pass


def render():
    clear_canvas()
    image.draw(get_canvas_width() // 2, get_canvas_height() // 2)
    update_canvas()
