import unittest
from types import SimpleNamespace
from unittest.mock import patch

import pico2d
import ball
import boy
import grass
import game_framework
import game_world
import item_mode
import pause_mode
import play_mode
import title_mode


class ItemModeTests(unittest.TestCase):
    def setUp(self):
        self.clock = 10.0
        for module in (ball, boy, grass, item_mode, title_mode):
            patcher = patch.object(module, 'load_image', side_effect=lambda path: SimpleNamespace(path=path))
            patcher.start()
            self.addCleanup(patcher.stop)
        for module in (boy, play_mode):
            patcher = patch.object(module, 'get_time', side_effect=lambda: self.clock)
            patcher.start()
            self.addCleanup(patcher.stop)
        ball.Ball.images.clear()
        game_framework.running = True
        game_framework.stack = [play_mode]
        play_mode.init()
        self.addCleanup(self.finish_modes)

    def finish_modes(self):
        while game_framework.stack:
            game_framework.stack.pop().finish()

    def key(self, mode, key):
        event = SimpleNamespace(type=pico2d.SDL_KEYDOWN, key=key)
        with patch.object(mode, 'get_events', return_value=[event]):
            mode.handle_events()

    def test_selection_controls_projectiles(self):
        player = play_mode.boy
        self.key(play_mode, pico2d.SDLK_i)
        for selection in (0, 1, 2):
            self.key(item_mode, pico2d.SDLK_0 + selection)
            self.assertEqual(player.item, selection)
            before = len(game_world.world[1])
            player.fire_ball()
            self.assertEqual(len(game_world.world[1]), before + (selection != 0))
        small, large = game_world.world[1][-2:]
        self.assertEqual(small.image.path, 'ball21x21.png')
        self.assertEqual(large.image.path, 'ball41x41.png')

    def test_return_preserves_world_and_pauses_idle_timer(self):
        player = play_mode.boy
        player.x = 123
        player.fire_ball()
        snapshot = [list(layer) for layer in game_world.world]
        self.key(play_mode, pico2d.SDLK_i)
        self.clock += 20
        with patch.object(game_world, 'update') as update:
            item_mode.update()
            update.assert_not_called()
        self.key(item_mode, pico2d.SDLK_i)
        self.assertEqual(game_framework.stack, [play_mode])
        self.assertIs(play_mode.boy, player)
        self.assertEqual(player.x, 123)
        self.assertEqual(game_world.world, snapshot)
        self.assertEqual(player.idle_started_at, self.clock)

    def test_title_return_resets_selection_and_world(self):
        original = play_mode.boy
        original.item = 2
        original.fire_ball()
        self.key(play_mode, pico2d.SDLK_ESCAPE)
        self.assertTrue(all(not layer for layer in game_world.world))
        self.key(title_mode, pico2d.SDLK_SPACE)
        self.assertIsNot(play_mode.boy, original)
        self.assertEqual(play_mode.boy.item, 1)

    def test_pause_toggle_still_preserves_player(self):
        original = play_mode.boy
        with patch.object(pause_mode, 'load_font', return_value=object()):
            self.key(play_mode, pico2d.SDLK_p)
        self.assertIs(game_framework.stack[-1], pause_mode)
        self.key(pause_mode, pico2d.SDLK_p)
        self.assertIs(play_mode.boy, original)
        self.assertEqual(game_framework.stack, [play_mode])


    def test_menu_ignores_gameplay_keys_and_closes_window(self):
        self.key(play_mode, pico2d.SDLK_i)
        player = play_mode.boy
        before = [list(layer) for layer in game_world.world]
        for key in (pico2d.SDLK_SPACE, pico2d.SDLK_RIGHT, pico2d.SDLK_p):
            self.key(item_mode, key)
        self.assertEqual(game_framework.stack, [play_mode, item_mode])
        self.assertEqual(game_world.world, before)
        self.assertEqual(player.pressed_keys, set())
        with patch.object(item_mode, 'get_events', return_value=[SimpleNamespace(type=pico2d.SDL_QUIT)]):
            item_mode.handle_events()
        self.assertFalse(game_framework.running)

    def test_repeated_menu_visits_preserve_selection_without_stacking(self):
        player = play_mode.boy
        for _ in range(3):
            self.key(play_mode, pico2d.SDLK_i)
            self.assertEqual(len(game_framework.stack), 2)
            self.key(item_mode, pico2d.SDLK_2)
            self.key(item_mode, pico2d.SDLK_i)
            self.assertEqual(game_framework.stack, [play_mode])
            self.assertIs(play_mode.boy, player)
            self.assertEqual(player.item, 2)

if __name__ == '__main__':
    unittest.main()

