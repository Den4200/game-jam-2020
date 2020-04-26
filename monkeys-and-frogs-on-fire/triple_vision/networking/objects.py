import json
import socket
from typing import Any, Dict, List, Optional

import numpy as np


class Player:

    def __init__(
        self,
        id: str,
        username: str,
        pos: List[float] = [0, 0],
        curr_color: str = 'red',
        hp: float = 1000,
        conn: Optional[socket.socket] = None,
        target_pos: Optional[List[float]] = None
    ) -> None:
        self.id = id
        self.username = username
        self.hp = hp
        self.pos = pos
        self.target_pos = target_pos
        self.curr_color = curr_color

        self.conn = conn

    def serialize(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'username': self.username,
            'hp': self.hp,
            'target_pos': self.target_pos,
            'pos': self.pos,
            'curr_color': self.curr_color
        }


class Projectile:

    def __init__(self, start_pos: List[float], angle: float, color: str) -> None:
        self.start_pos = start_pos
        self.angle = angle
        self.color = color

    def serialize(self) -> Dict[str, Any]:
        return {
            'start_pos': self.start_pos,
            'angle': self.angle,
            'color': self.angle
        }


class Enemy:

    def __init__(
        self,
        pos: List[float],
        type: str,
        hp: float,
        target_pos: Optional[List[float]] = None
    ) -> None:
        self.pos = pos
        self.hp = hp
        self.target_pos = target_pos
        self.type = type

    def serialize(self) -> Dict[str, Any]:
        return {
            'pos': self.pos,
            'hp': self.hp,
            'target_pos': self.target_pos,
            'type': self.type
        }


class GameState:
    players: List[Player] = list()

    slow_mo: bool = False

    projectiles: List[Dict[str, Any]] = list()

    enemies: List[Dict[str, Any]] = list()

    map: List[List[int]] = list()

    is_online: bool = True

    @classmethod
    def serialize(cls) -> str:
        return json.dumps({
            'players': [
                player.serialize() for player in cls.players
            ],
            'slow_mo': cls.slow_mo,
            'projectiles': [
                projectile.serialize() for projectile in cls.projectiles
            ],
            'enemies': [
                enemy.serialize() for enemy in cls.enemies
            ],
            'map': [list(arr) for arr in cls.map]
        })

    @classmethod
    def unserialize(cls, data) -> None:
        data = json.loads(data)

        cls.players = [Player(**p) for p in data['players']]
        cls.slow_mo = data['slow_mo']
        cls.projectiles = [Projectile(**p) for p in data['projectiles']]
        cls.enemies = [Enemy(**e) for e in data['enemies']]
        cls.map = np.array(data['map'])
