from serpent.game import Game

from .api.api import HorizonChaseTurboAPI

from .environments.race_environment import RaceEnvironment
from .environments.common import WorldRegions

from serpent.utilities import Singleton

import time


class SerpentHorizonChaseTurboGame(Game, metaclass=Singleton):

    def __init__(self, **kwargs):
        kwargs["platform"] = "steam"

        kwargs["window_name"] = "HorizonChaseTurbo"

        kwargs["app_id"] = "389140"
        kwargs["app_args"] = None

        super().__init__(**kwargs)

        self.api_class = HorizonChaseTurboAPI
        self.api_instance = None

        self.environments = {
            "RACE": RaceEnvironment
        }

        self.environment_data = {
            "WORLD_REGIONS": WorldRegions
        }

        self.frame_transformation_pipeline_string = "RESIZE:100x100|GRAYSCALE|FLOAT"

    @property
    def screen_regions(self):
        regions = {
            "UI_POSITION": (34, 17, 106, 139),
            "UI_SPEED": (32, 729, 108, 904),
            "UI_OUT_OF_FUEL": (227, 394, 257, 631),
            "UI_FUEL_PIP_1": (203, 873, 220, 880),
            "UI_FUEL_PIP_2": (203, 884, 220, 890),
            "UI_FUEL_PIP_3": (203, 895, 220, 901),
            "UI_FUEL_PIP_4": (203, 906, 220, 912),
            "UI_FUEL_PIP_5": (203, 917, 220, 923),
            "UI_FUEL_PIP_6": (203, 928, 220, 934),
            "UI_FUEL_PIP_7": (203, 939, 220, 945),
            "UI_FUEL_PIP_8": (203, 950, 220, 956),
            "UI_FUEL_PIP_9": (203, 961, 220, 967),
            "WORLD_MAP_CALIFORNIA": (302, 516, 322, 584),
            "WORLD_MAP_CHILE": (419, 604, 438, 673),
            "WORLD_MAP_BRAZIL": (383, 614, 403, 696),
            "WORLD_MAP_SOUTH_AFRICA": (419, 612, 437, 695),
            "WORLD_MAP_GREECE": (362, 646, 384, 739),
            "WORLD_MAP_ICELAND": (327, 612, 349, 710),
            "WORLD_MAP_UAE": (362, 632, 383, 740),
            "WORLD_MAP_INDIA": (333, 618, 354, 680),
            "WORLD_MAP_AUSTRALIA": (437, 591, 459, 689),
            "WORLD_MAP_CHINA": (304, 628, 327, 700),
            "WORLD_MAP_JAPAN": (325, 609, 347, 693),
            "WORLD_MAP_HAWAII": (347, 626, 367, 700)
        }

        return regions
