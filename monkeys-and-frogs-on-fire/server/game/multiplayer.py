import random
from typing import Any, Dict

from frost.ext import Cog
from frost.server import auth_required, Memory
from frost.server.database import managed_session, User

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
        with managed_session() as session:
            user = session.query(User).filter(User.id == id_).first()
            username = user.username

        user = Memory.logged_in_users[id_]
        GameState.players.append(Player(id_, username, conn=user.conn))

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

        collision_list = list()
        other_list = list()

        for i in range(s.MAP_SIZE[0]):
            for j in range(s.MAP_SIZE[1]):
                val = GameState.map[i][j]

                if val == Map.AIR:
                    continue

                if val == Map.WALL:
                    collision_list.append(val)

                else:
                    other_list.append((i, j, val))

        for player in GameState.players:
            while True:
                center = (random.randrange(0, s.MAP_SIZE[0]), random.randrange(0, s.MAP_SIZE[1]))

                if (
                    all(
                        tile[0] != center[0] and tile[1] != center[1] and tile[2] for tile in collision_list
                    ) and
                    any(
                        tile[0] == center[0] and tile[1] == center[1] and tile[2] for tile in other_list
                    )
                ):
                    break

            player.pos[0] = center[0]
            player.pos[1] = center[1] + s.PLAYER_CENTER_Y_COMPENSATION

        for (enemy_type, enemy_hp) in Enemies:
            for _ in range(5):
                while True:
                    center = tile_to_pixels(random.randrange(0, s.MAP_SIZE[0]), random.randrange(0, s.MAP_SIZE[1]))

                    if (
                        all(
                            tile[0] != center[0] and tile[1] != center[1] and tile[2] for tile in collision_list
                        ) and
                        any(
                            tile[0] == center[0] and tile[1] == center[1] and tile[2] for tile in other_list
                        )
                    ):
                        break

                GameState.enemies.append(Enemy(center, enemy_type, enemy_hp))

        serizalized_game_state = GameState.serialize()

        for player in GameState.players:
            kwargs['send'](player.conn, {
                'headers': {
                    'path': 'multiplayer/start_game'
                },
                'game_state': serizalized_game_state
            })
