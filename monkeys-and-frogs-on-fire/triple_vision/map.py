import random
from typing import Optional, Tuple

import arcade
import numpy as np

from triple_vision import Settings as s
from triple_vision.entities import Spike
from triple_vision.utils import tile_to_pixels


random.seed(1)


class Map:
    AIR = 0
    WALL = 1
    FLOOR = 2
    SPIKE = 3

    GENERATIONS = 6
    FILL_PROBABILITY = 0.2
    SPIKE_PROBABILITY = 0.01

    def __init__(self, view: arcade.View, shape: Tuple[int, int]) -> None:
        self.view = view
        self.shape = shape

        self.sprites: Optional[arcade.SpriteList] = None

    @classmethod
    def generate(cls, shape) -> np.array:
        map_ = np.ones(shape)

        for i in range(shape[0]):
            for j in range(shape[1]):
                choice = random.uniform(0, 1)
                map_[i][j] = cls.WALL \
                    if choice < cls.FILL_PROBABILITY else cls.FLOOR

        for gen in range(cls.GENERATIONS):
            for i in range(shape[0]):
                for j in range(shape[1]):

                    # Get walls that are 1 away from each index
                    submap = map_[
                        max(i - 1, 0): min(i + 2, map_.shape[0]),
                        max(j - 1, 0): min(j + 2, map_.shape[1])
                    ]
                    flat_submap = submap.flatten()
                    wall_count_1_away = len(np.where(flat_submap == cls.WALL)[0])
                    floor_count_1_away = len(np.where((flat_submap == cls.FLOOR) | (flat_submap == cls.SPIKE))[0])

                    # Get walls that are 2 away from each index
                    submap = map_[
                        max(i - 2, 0): min(i + 3, map_.shape[0]),
                        max(j - 2, 0): min(j + 3, map_.shape[1])
                    ]
                    wall_count_2_away = len(np.where(submap.flatten() == cls.WALL)[0])

                    # First (self.GENERATIONS - 1) generations build scaffolding for walls
                    if gen < cls.GENERATIONS - 1:

                        # If 1 away has 5 or more walls, make the current point a wall
                        # If 2 away has 7 or more walls, make the current point a wall
                        # If neither, make the current point floor
                        if wall_count_1_away >= 5 or wall_count_2_away <= 7:
                            map_[i][j] = cls.WALL
                        else:
                            chance = random.uniform(0, 1)
                            map_[i][j] = cls.FLOOR \
                                if chance > cls.SPIKE_PROBABILITY else cls.SPIKE

                        # Make the current point a wall if it's on the edge of the map
                        if i == 0 or j == 0 or i == shape[0] - 1 or j == shape[1] - 1:
                            map_[i][j] = cls.WALL

                    else:
                        # Turn all walls that aren't near floor into air
                        if floor_count_1_away == 0 and map_[i][j] == cls.WALL:
                            map_[i][j] = cls.AIR

        return map_

    def spritify(self, map_) -> Tuple[arcade.SpriteList, arcade.SpriteList, arcade.SpriteList]:
        spikes = arcade.SpriteList(use_spatial_hash=True)
        sprites = arcade.SpriteList(use_spatial_hash=True)
        collision_list = arcade.SpriteList(use_spatial_hash=True)

        for i in range(self.shape[0]):
            for j in range(self.shape[1]):
                val = map_[i][j]

                if val == self.AIR:
                    continue

                center_x, center_y = tile_to_pixels(i, j)

                if val == self.SPIKE:
                    sprite = Spike(
                        ctx=self.view.game_manager,
                        target_player=self.view.player,
                        target_enemies=None,
                        scale=s.SCALING,
                        center_x=center_x,
                        center_y=center_y,
                        spawn_in_map=False
                    )
                    spikes.append(sprite)

                else:
                    filename = 'wall_mid' \
                        if val == self.WALL else f'floor_{random.randint(1, 8)}'

                    sprite = arcade.Sprite(
                        filename=f'assets/dungeon/frames/{filename}.png',
                        scale=s.SCALING,
                        center_x=center_x,
                        center_y=center_y
                    )

                    if val == self.WALL:
                        collision_list.append(sprite)

                sprites.append(sprite)

        return sprites, collision_list, spikes

    @classmethod
    def ensure_generate(cls, shape: Tuple[int, int]) -> np.array:
        floor_count = 0
        map_ = None

        while floor_count < (shape[0] * shape[1]) / 2.5:
            map_ = cls.generate(shape)
            flat_map = map_.flatten()
            floor_count = len(np.where((flat_map == cls.FLOOR) | (flat_map == cls.SPIKE))[0])

        return map_

    def setup(self, map_: Optional[np.array] = None) -> None:
        if not map_:
            map_ = self.ensure_generate(self.shape)
        self.sprites, self.view.collision_list, self.view.game_manager.spikes = self.spritify(map_)

    def draw(self) -> None:
        self.sprites.draw()

    def on_update(self, delta_time: float = 1/60) -> None:
        self.sprites.on_update(delta_time)
