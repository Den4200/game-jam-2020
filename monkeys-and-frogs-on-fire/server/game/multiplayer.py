import random
from typing import Any, Dict

import arcade
from frost.ext import Cog
from frost.server import auth_required, logger, Memory, Status

from server.game.objects import Enemy, GameState
from triple_vision import Settings as s
from triple_vision.managers import LevelManager
from triple_vision.map import Map
from triple_vision.utils import tile_to_pixels


class Multiplayer(Cog, route='multiplayer'):

    @auth_required
    def join(
        data: Dict[str, Any],
        token: str,
        id_: str,
        **kwargs: Any
    ) -> None:
        user = Memory.logged_in_users[id_]
        GameState.player_conns.append({
            'id': id_,
            'username': user.username,
            'conn': user.conn
        })

        logger.info(f'User {user.username} joined the game')

    @auth_required
    def start_game(
        data: Dict[str, Any],
        token: str,
        id_: str,
        **kwargs: Any
    ) -> None:
        GameState.map = Map.ensure_generate(s.MAP_SIZE)

        collision_list = arcade.SpriteList(use_spatial_hash=True, is_static=True)
        other_list = arcade.SpriteList(use_spatial_hash=True, is_static=True)

        for i in range(s.MAP_SIZE[0]):
            for j in range(s.MAP_SIZE[1]):
                val = GameState.map[i][j]
                px = tile_to_pixels(i, j)

                if val == Map.AIR:
                    continue

                if val == Map.WALL:
                    collision_list.append(
                        arcade.Sprite(
                            filename='assets/dungeon/frames/wall_corner_front_left.png',
                            scale=s.SCALING,
                            center_x=px[0],
                            center_y=px[1]
                        )
                    )

                else:
                    other_list.append(
                        arcade.Sprite(
                            filename='assets/dungeon/frames/floor_1.png',
                            scale=s.SCALING,
                            center_x=px[0],
                            center_y=px[1]
                        )
                    )

        center = find_free_tile(collision_list, other_list)
        GameState.player.pos[0] = center[0]
        GameState.player.pos[1] = center[1] + s.PLAYER_CENTER_Y_COMPENSATION

        level_stats = LevelManager.create_level_stats(1)

        for level in level_stats:
            for _ in range(int(level['amount'])):
                GameState.enemies.append(
                    Enemy(
                        find_free_tile(collision_list, other_list),
                        **level
                    )
                )

        serizalized_game_state = GameState.serialize()

        for player in GameState.player_conns:
            kwargs['send'](player['conn'], {
                'headers': {
                    'path': 'multiplayer/start_game',
                    'status': Status.SUCCESS.value
                },
                'game_state': serizalized_game_state
            })

        logger.info(f'Players: {", ".join(player["username"] for player in GameState.player_conns)}')
        logger.info('Game started!')


def find_free_tile(collision_list, other_list):
    while True:
        center = tile_to_pixels(random.randrange(0, s.MAP_SIZE[0]), random.randrange(0, s.MAP_SIZE[1]))

        if (
            len(arcade.get_sprites_at_point(center, collision_list)) == 0 and
            len(arcade.get_sprites_at_point(center, other_list)) > 0
        ):
            return center
