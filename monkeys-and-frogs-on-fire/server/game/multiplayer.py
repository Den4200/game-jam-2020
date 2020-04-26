import random
from typing import Any, Dict

import arcade
from frost.ext import Cog
from frost.server import auth_required, logger, Memory, Status

from server.game.objects import Enemy, GameState, Player, Projectile
from triple_vision import Settings as s
from triple_vision.entities import Enemies
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
        GameState.players.append(Player(id_, user.username, conn=user.conn))

        logger.info(f'User {user.username} joined the game')

    @auth_required
    def player_target_pos(
        data: Dict[str, Any],
        token: str,
        id_: str,
        **kwargs: Any
    ) -> None:
        for player in GameState.players:
            if player.id == id_:
                player.target_pos = data['target_pos']
                continue

            kwargs['send'](player.conn, {
                'headers': {
                    'path': 'multiplayer/player_target_pos'
                },
                'id': id_,
                'target_pos': data['target_pos']
            })

    @auth_required
    def player_change_color(
        data: Dict[str, Any],
        token: str,
        id_: str,
        **kwargs: Any
    ) -> None:
        for player in GameState.players:
            if player.id == id_:
                player.color = data['color']
                continue

            kwargs['send'](player.conn, {
                'headers': {
                    'path': 'multiplayer/player_change_color'
                },
                'id': id_,
                'color': data['color']
            })

    @auth_required
    def fire_projectile(
        data: Dict[str, Any],
        token: str,
        id_: str,
        **kwargs: Any
    ) -> None:
        proj = Projectile(**data['projectile'])
        GameState.projectiles.append(proj)

        for player in GameState.players:
            if player.id == id_:
                continue

            kwargs['send'](player.conn, {
                'headers': {
                    'path': 'multiplayer/fire_projectile'
                },
                'projectile': data['projectile']
            })

    @auth_required
    def slow_mo(
        data: Dict[str, Any],
        token: str,
        id_: str,
        **kwargs: Any
    ) -> None:
        GameState.slow_mo = data['slow_mo']

        for player in GameState.players:
            if player.id == id_:
                continue

            kwargs['send'](player.conn, {
                'headers': {
                    'path': 'multiplayer/slow_mo'
                },
                'slow_mo': data['slow_mo']
            })

    @auth_required
    def start_game(
        data: Dict[str, Any],
        token: str,
        id_: str,
        **kwargs: Any
    ) -> None:
        GameState.map = Map.ensure_generate(s.MAP_SIZE)
        print(GameState.map)

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

        for player in GameState.players:
            center = find_free_tile(collision_list, other_list)
            player.pos[0] = center[0]
            player.pos[1] = center[1] + s.PLAYER_CENTER_Y_COMPENSATION

        for enemy in Enemies:
            for _ in range(5):
                # print(_)
                GameState.enemies.append(
                    Enemy(
                        find_free_tile(collision_list, other_list),
                        enemy.name,
                        enemy.value
                    )
                )

        serizalized_game_state = GameState.serialize()

        for player in GameState.players:
            kwargs['send'](player.conn, {
                'headers': {
                    'path': 'multiplayer/start_game',
                    'status': Status.SUCCESS.value
                },
                'game_state': serizalized_game_state
            })

        logger.info(f'Players: {", ".join(player.username for player in GameState.players)}')
        logger.info('Game started!')


def find_free_tile(collision_list, other_list):
    while True:
        center = tile_to_pixels(random.randrange(0, s.MAP_SIZE[0]), random.randrange(0, s.MAP_SIZE[1]))
        # print(center)

        if (
            len(arcade.get_sprites_at_point(center, collision_list)) == 0 and
            len(arcade.get_sprites_at_point(center, other_list)) > 0
        ):
            return center
