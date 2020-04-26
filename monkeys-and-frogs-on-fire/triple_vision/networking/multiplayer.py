from typing import Any, Dict

from frost.client.events import EventStatus
from frost.ext import Cog
from triple_vision.networking.objects import GameState, Projectile


class Multiplayer(Cog, route='multiplayer'):

    def player_target_pos(data: Dict[str, Any]) -> None:
        for player in GameState.players:
            if player.id == data['id']:
                player.target_pos = data['target_pos']
                break

    def player_change_color(data: Dict[str, Any]) -> None:
        for player in GameState.players:
            if player.id == data['id']:
                player.color = data['color']
                break

    def fire_projectile(data: Dict[str, Any]) -> None:
        GameState.projectiles.append(Projectile(**data['projectile']))

    def slow_mo(data: Dict[str, Any]) -> None:
        GameState.slow_mo = data['slow_mo']

    def start_game(data: Dict[str, Any]) -> None:
        GameState.unserialize(data['game_state'])
        EventStatus.start_game = data['headers']['status']
