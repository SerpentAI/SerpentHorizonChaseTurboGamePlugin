from serpent.environment import Environment

from serpent.input_controller import KeyboardKey

from serpent.utilities import SerpentError

import time
import collections

import numpy as np


class RaceEnvironment(Environment):

    def __init__(self, game_api=None, input_controller=None, episodes_per_race_track=5):
        super().__init__("Race Environment", game_api=game_api, input_controller=input_controller)

        self.episodes_per_race_track = episodes_per_race_track

        self.reset()

    @property
    def new_episode_data(self):
        return {}

    @property
    def end_episode_data(self):
        return {}

    def new_episode(self, maximum_steps=None, reset=False):
        self.reset_game_state()

        time.sleep(1)

        if (self.episode + 1) % self.episodes_per_race_track == 0:
            self.input_controller.tap_key(KeyboardKey.KEY_ENTER)
        else:
            self.input_controller.tap_key(KeyboardKey.KEY_R)

        time.sleep(8)

        super().new_episode(maximum_steps=maximum_steps, reset=reset)

    def end_episode(self):
        super().end_episode()

    def reset(self):
        self.reset_game_state()
        super().reset()

    def reset_game_state(self):
        self.game_state = {
            "previous_speed": 0,
            "current_speed": 0,
            "average_speed": 0,
            "speeds": collections.deque(np.full((40,), 300), maxlen=40),
            "fuel_levels": collections.deque(np.full((40,), 10), maxlen=40),
            "is_too_slow": False,
            "is_out_of_fuel": False,
            "is_race_over": False
        }

    def update_game_state(self, game_frame):
        self.game_state["previous_speed"] = self.game_state["current_speed"]

        speed = self.game_api.parse_speed(game_frame)

        self.game_state["current_speed"] = speed if speed is not None else self.game_state["previous_speed"]
        self.analytics_client.track(event_key="CAR_SPEED", data={"speed": self.game_state["current_speed"]})

        self.game_state["speeds"].appendleft(self.game_state["current_speed"])
        self.game_state["average_speed"] = int(np.mean(self.game_state["speeds"]))

        self.analytics_client.track(event_key="CAR_SPEED_AVERAGE", data={"speed": self.game_state["average_speed"]})

        self.game_state["fuel_levels"].appendleft(self.game_api.parse_fuel(game_frame))

        self.game_state["is_too_slow"] = self.game_state["average_speed"] < 20.0

        self.game_state["is_out_of_fuel"] = self.game_api.is_out_of_fuel(game_frame)
        self.game_state["is_race_over"] = self.game_api.is_race_over(game_frame)

        return True
