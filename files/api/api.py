from serpent.game_api import GameAPI

from serpent.input_controller import KeyboardKey, KeyboardEvent, KeyboardEvents
from serpent.input_controller import MouseButton, MouseEvent, MouseEvents

from serpent.frame_grabber import FrameGrabber

import serpent.cv

import numpy as np

import skimage.io
import skimage.util
import skimage.morphology
import skimage.segmentation
import skimage.measure

import math
import time
import random

from ..environments.common import WorldRegions


digit_floored_centroids = {
    (24, 11): 1,
    (28, 27): 2,
    (26, 30): 3,
    (22, 26): 4,
    (24, 26): 5,
    (27, 23): 6,
    (17, 21): 7,
    (26, 25): 8,
    (25, 27): 9
}

fuel_pip_colors = {
    1: (243, 18, 82),
    2: (251, 48, 38),
    3: (255, 84, 15),
    4: (255, 123, 15),
    5: (255, 154, 15),
    6: (255, 159, 15),
    7: (255, 159, 15),
    8: (255, 159, 15),
    9: (255, 159, 15)
}

class HorizonChaseTurboAPI(GameAPI):
    def __init__(self, game=None):
        super().__init__(game=game)

        self.world_map_sprites_keys = [
            'SPRITE_WORLD_MAP_AUSTRALIA',
            'SPRITE_WORLD_MAP_BRAZIL',
            'SPRITE_WORLD_MAP_CALIFORNIA',
            'SPRITE_WORLD_MAP_CHILE',
            'SPRITE_WORLD_MAP_CHINA',
            'SPRITE_WORLD_MAP_GREECE',
            'SPRITE_WORLD_MAP_HAWAII',
            'SPRITE_WORLD_MAP_ICELAND',
            'SPRITE_WORLD_MAP_INDIA',
            'SPRITE_WORLD_MAP_JAPAN',
            'SPRITE_WORLD_MAP_SOUTH_AFRICA',
            'SPRITE_WORLD_MAP_UAE'
        ]

        self.next_region_inputs = [
            KeyboardKey.KEY_S,
            KeyboardKey.KEY_D,
            KeyboardKey.KEY_D,
            KeyboardKey.KEY_W,
            KeyboardKey.KEY_W,
            KeyboardKey.KEY_D,
            KeyboardKey.KEY_D,
            KeyboardKey.KEY_D,
            KeyboardKey.KEY_W,
            KeyboardKey.KEY_D,
            KeyboardKey.KEY_D,
            KeyboardKey.KEY_D
        ]

        self.game_inputs = {
            "STEERING": {
                "STEER LEFT": [
                    KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_A)
                ],
                "ACCELERATE - STEER LEFT": [
                    KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_A),
                    KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_W)
                ],
                "ACCELERATE": [
                    KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_W)
                ],
                "ACCELERATE - STEER RIGHT": [
                    KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_W),
                    KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_D)
                ],
                "STEER RIGHT": [
                    KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_D)
                ],
                "BRAKE": [
                    KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_S)
                ],
                "NITRO": [
                    KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_SPACE)
                ],
                "IDLE": []
            }
        }

    def parse_speed(self, game_frame):
        region_image = serpent.cv.extract_region_from_image(
            game_frame.frame,
            self.game.screen_regions["UI_SPEED"]
        )

        return self.parse_digits(region_image)

    def parse_digits(self, image):
        bw_image = skimage.util.img_as_ubyte(np.all(image > 252, axis=-1))
        bw_image = skimage.morphology.closing(bw_image, skimage.morphology.rectangle(8, 1))

        cleared_bw_image = skimage.segmentation.clear_border(bw_image)
        label_image = skimage.measure.label(cleared_bw_image)

        result = ""

        for region in skimage.measure.regionprops(label_image):
            if region.area >= 100:
                floored_centroid = tuple([math.floor(i) for i in region.local_centroid])

                if floored_centroid == (26, 25):
                    result += str(8 if region.area > 1600 else 0)
                else:
                    digit = digit_floored_centroids.get(floored_centroid)

                    if digit is None:
                        result = None
                        break
                    else:
                        result += str(digit)

        return None if result in [None, ""] else int(result)

    def parse_fuel(self, game_frame):
        current_fuel_level = 1

        for i in range(1, 10):
            fuel_pip_image = serpent.cv.extract_region_from_image(game_frame.frame, self.game.screen_regions[f"UI_FUEL_PIP_{i}"])
            fuel_pip_color = tuple(fuel_pip_image[10, 2, :])

            if fuel_pip_color != fuel_pip_colors[i]:
                return current_fuel_level
            
            current_fuel_level += 1

        return current_fuel_level

    def is_out_of_fuel(self, game_frame):
        reference = np.squeeze(self.game.sprites["SPRITE_UI_OUT_OF_FUEL"].image_data)
        region = serpent.cv.extract_region_from_image(game_frame.frame, self.game.screen_regions["UI_OUT_OF_FUEL"])

        ssim = skimage.measure.compare_ssim(reference, region, multichannel=True)

        return ssim > 0.9

    def is_race_over(self, game_frame):
        region = serpent.cv.extract_region_from_image(game_frame.frame, self.game.screen_regions["UI_SPEED"])
        bw_region = skimage.util.img_as_ubyte(np.all(region > 252, axis=-1))

        white_pixel_count = bw_region[bw_region > 0].size

        return white_pixel_count < 500

    def select_random_track(self, input_controller):
        input_controller.handle_keys([])

        start_world_region = None

        while start_world_region is None:
            game_frame_buffer = FrameGrabber.get_frames([0])
            game_frame = game_frame_buffer.frames[0]

            start_world_region = self.identify_world_region(game_frame)

        end_world_region = random.choice(range(0, 9))

        self.go_to_world_region(start_world_region, end_world_region, input_controller)

        input_controller.tap_key(KeyboardKey.KEY_ENTER)
        time.sleep(1)

        possible_keys = [
            KeyboardKey.KEY_W,
            KeyboardKey.KEY_A,
            KeyboardKey.KEY_S,
            KeyboardKey.KEY_D
        ]

        for _ in range(30):
            input_controller.tap_key(random.choice(possible_keys))
            time.sleep(0.05)

        input_controller.tap_key(KeyboardKey.KEY_ENTER)
        time.sleep(1)

        possible_keys = [
            KeyboardKey.KEY_A,
            KeyboardKey.KEY_D
        ]

        for _ in range(30):
            input_controller.tap_key(random.choice(possible_keys))
            time.sleep(0.05)

        input_controller.tap_key(KeyboardKey.KEY_ENTER)
        time.sleep(1)

    def select_random_region_track(self, input_controller):
        input_controller.handle_keys([])

        possible_keys = [
            KeyboardKey.KEY_W,
            KeyboardKey.KEY_A,
            KeyboardKey.KEY_S,
            KeyboardKey.KEY_D
        ]

        for _ in range(30):
            input_controller.tap_key(random.choice(possible_keys))
            time.sleep(0.05)

        input_controller.tap_key(KeyboardKey.KEY_ENTER)
        time.sleep(1)

        possible_keys = [
            KeyboardKey.KEY_A,
            KeyboardKey.KEY_D
        ]

        for _ in range(30):
            input_controller.tap_key(random.choice(possible_keys))
            time.sleep(0.05)

        input_controller.tap_key(KeyboardKey.KEY_ENTER)
        time.sleep(1)

    def identify_world_region(self, game_frame):
        world_region = None

        for world_map_sprites_key in self.world_map_sprites_keys:
            sprite = self.game.sprites[world_map_sprites_key]
            reference_image = np.squeeze(sprite.image_data)

            screen_region_name = world_map_sprites_key.replace("SPRITE_", "")
            region_image = serpent.cv.extract_region_from_image(game_frame.frame, self.game.screen_regions[screen_region_name])

            ssim = skimage.measure.compare_ssim(reference_image, region_image, multichannel=True)

            if ssim > 0.9:
                world_region = world_map_sprites_key.replace("SPRITE_WORLD_MAP_", "")
                break

        return WorldRegions[world_region] if world_region is not None else None

    def go_to_world_region(self, start_world_region, end_world_region, input_controller):
        world_region_index = start_world_region.value

        while world_region_index != end_world_region:
            input_controller.tap_key(self.next_region_inputs[world_region_index])

            world_region_index += 1

            if world_region_index > 11:
                world_region_index = 0

            time.sleep(0.1)

        time.sleep(0.5)
