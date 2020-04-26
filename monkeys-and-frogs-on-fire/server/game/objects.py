import json
from typing import Any, Dict, List, Tuple

import numpy as np


class Player:

    def __init__(
        self,
        pos: List[float] = [0, 0],
        hp: float = 1000,
        is_alive: bool = True
    ) -> None:
        self.hp = hp
        self.is_alive = is_alive
        self.pos = pos

    def serialize(self) -> Dict[str, Any]:
        return {
            'is_alive': self.is_alive,
            'hp': self.hp,
            'pos': self.pos
        }


class Enemy:

    def __init__(
        self,
        pos: List[float],
        type: Tuple[str, str],
        detection_radius: float,
        moving_speed: float = 0,
        shoot_interval: float = 0,
        dmg: float = 0,
        hp: float = 0,
        **kwargs: Any
    ) -> None:
        self.pos = pos
        self.dmg = dmg
        self.type = type
        self.hp = hp
        self.moving_speed = moving_speed
        self.detection_radius = detection_radius
        self.shoot_interval = shoot_interval

    def serialize(self) -> Dict[str, Any]:
        return {
            'pos': self.pos,
            'dmg': self.dmg,
            'type': self.type,
            'hp': self.hp,
            'moving_speed': self.moving_speed,
            'detection_radius': self.detection_radius,
            'shoot_interval': self.shoot_interval
        }


class GameState:
    player_conns: List[Dict[str, Any]] = list()

    player: Player = Player()

    enemies: List[Dict[str, Any]] = list()

    map: List[List[int]] = list()

    is_online: bool = True

    @classmethod
    def serialize(cls) -> str:
        return json.dumps({
            'player': cls.player.serialize(),
            'enemies': [
                enemy.serialize() for enemy in cls.enemies
            ],
            'map': [list(arr) for arr in cls.map]
        })

    @classmethod
    def unserialize(cls, data) -> None:
        data = json.loads(data)

        cls.player = Player(**data['player'])
        cls.enemies = [Enemy(**e) for e in data['enemies']]
        cls.map = np.array(data['map'])
