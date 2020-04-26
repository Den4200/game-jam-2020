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
    def start_game(self, token: str, id_: str) -> None:
        self.send({
            'headers': {
                'path': 'multiplayer/start_game',
                'token': token,
                'id': id_
            }
        })
