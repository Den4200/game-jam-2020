from typing import Tuple

from frost import FrostClient
from frost.client import get_auth

from triple_vision.networking.multiplayer import Multiplayer
from triple_vision.networking.scores import Scores


class Client(FrostClient):

    def __init__(self, ip: str = '127.0.0.1', port: int = 5555) -> None:
        super().__init__(ip, port)

        # Load up cogs
        Scores()
        Multiplayer()

    @get_auth
    def new_score(self, score: int, token: str, id_: str) -> None:
        self.send({
            'headers': {
                'path': 'scores/new',
                'id': id_,
                'token': token
            },
            'score': score
        })

    @get_auth
    def get_top_scores(self, token: str, id_: str) -> None:
        self.send({
            'headers': {
                'path': 'scores/get_top',
                'id': id_,
                'token': token
            }
        })

    @get_auth
    def join_game(self, token: str, id_: str) -> None:
        self.send({
            'headers': {
                'path': 'multiplayer/join',
                'token': token,
                'id': id_
            }
        })

    @get_auth
    def send_target(self, target: Tuple[float, float], token: str, id_: str) -> None:
        self.send({
            'headers': {
                'path': 'multiplayer/player_target_pos',
                'token': token,
                'id': id_
            },
            'target_pos': target
        })

    @get_auth
    def send_color(self, color: str, token: str, id_: str) -> None:
        self.send({
            'headers': {
                'path': 'multiplayer/player_change_color',
                'token': token,
                'id': id_
            },
            'color': color
        })

    @get_auth
    def fire_projectile(
        self,
        start_pos: Tuple[float, float],
        angle: float,
        color: str,
        token: str,
        id_: str
    ) -> None:
        self.send({
            'headers': {
                'path': 'multiplayer/fire_projectile',
                'token': token,
                'id': id_
            },
            'projectile': {
                'start_pos': start_pos,
                'angle': angle,
                'color': color
            }
        })

    @get_auth
    def slow_mo(self, state: bool, token: str, id_: str) -> None:
        self.send({
            'headers': {
                'path': 'multiplayer/slow_mo',
                'token': token,
                'id': id_
            },
            'slow_mo': state
        })

    @get_auth
    def start_game(self, token: str, id_: str) -> None:
        self.send({
            'headers': {
                'path': 'multiplayer/start_game',
                'token': token,
                'id': id_
            }
        })
