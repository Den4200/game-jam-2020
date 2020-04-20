import enum
import time
from pathlib import Path

import arcade

from triple_vision import Settings as s
from triple_vision.entities.entities import LivingEntity
from triple_vision.entities.sprites import MovingSprite
from triple_vision.entities.weapons import LaserProjectile
from triple_vision.utils import is_in_radius


class Enemies(enum.Enum):
    """
    Key is base name of the image file.
    Value is default enemy health
    """
    big_demon = 1024
    imp = 512


class BaseEnemy(LivingEntity):
    enemy_assets_path = Path('assets/dungeon/frames')

    def __init__(self, enemy: Enemies, hp: int = 0, **kwargs) -> None:
        super().__init__(
            sprite_name=enemy.name,
            assets_path=self.enemy_assets_path,
            scale=s.SCALING,
            **kwargs
        )

        self.hp = enemy.value if hp < 1 else hp
        self.being_pushed = False


class ChasingEnemy(BaseEnemy, MovingSprite):
    """
    Simple chasing enemy that tries to catch some other sprite.
    No path-finding, just goes straight to sprite if it is in radius.
    """

    def __init__(
        self,
        ctx,
        enemy: Enemies,
        target_sprite: arcade.Sprite,
        detection_radius: int,
        **kwargs
    ) -> None:
        super().__init__(enemy, **kwargs)

        self.target_sprite = target_sprite
        self.detection_radius = detection_radius

    def update(self, delta_time: float = 1/60):
        if not self.being_pushed:
            if is_in_radius(self, self.target_sprite, self.detection_radius):
                self.move_to(self.target_sprite.center_x,
                             self.target_sprite.center_y,
                             rotate=False)
            else:
                self.change_x = 0
                self.change_y = 0

        super().update()


class StationaryEnemy(BaseEnemy):

    def __init__(
        self,
        ctx,
        enemy: Enemies,
        target_sprite: arcade.Sprite,
        detection_radius: int,
        **kwargs
    ) -> None:
        super().__init__(enemy, **kwargs)
        self.ctx = ctx

        self.target_sprite = target_sprite
        self.detection_radius = detection_radius

        self.last_shot = time.time()

    def update(self, delta_time: float = 1/60) -> None:
        if not is_in_radius(self, self.target_sprite, self.detection_radius):
            return

        if time.time() - self.last_shot < 0.75:  # TODO should be a constant
            return

        laser = LaserProjectile(
            center_x=self.center_x,
            center_y=self.center_y
        )
        laser.move_to(
            self.target_sprite.center_x,
            self.target_sprite.center_y,
            rotate=True,
            set_target=False
        )
        laser.play_activate_sound()

        self.ctx.enemy_projectiles.append(laser)
        self.last_shot = time.time()