from typing import Any, Dict

from frost.client.events import EventStatus
from frost.ext import Cog
from triple_vision.networking.objects import GameState


class Multiplayer(Cog, route='multiplayer'):

    def start_game(data: Dict[str, Any]) -> None:
        GameState.unserialize(data['game_state'])
        EventStatus.start_game = data['headers']['status']
