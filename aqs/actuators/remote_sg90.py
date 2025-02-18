import requests
from time import sleep

from aqs.actuators.actuator import Actuator, Action
from aqs.logger import LOGGER


class RemoteSG90Actuator(Actuator):
    def __init__(self, name, url):
        super().__init__(name)
        self._url = url
        
    def get_supported_actions(self):
        return [Action.ROTATE_DEG]

    def act(self, action: Action, value):
        if action != Action.ROTATE_DEG:
            LOGGER.error(
                f"[{self.get_name()}] [Remote SG90] Unsupported {action} action"
            )
            return False
        try:
            resp = self.__rotate(value)
            if resp.status_code != 200:
                LOGGER.error(
                    f"[{self.get_name()}] [Remote SG90] Failed to rotate: {resp.json()}"
                )
                return False
        except Exception as e:
            LOGGER.error(f"[{self.get_name()}] [Remote SG90] Action fail: {e}")
            return False
        return True

    def get_state(self):
        return self.__get_servo_angle()

    def is_alive(self):
        return self.__check_alive()

    def close(self):
        self.__close()

    # HTTP requests
    def __rotate(self, value):
        response = requests.post(f"{self._url}/rotate", json={"value": value})
        LOGGER.info(f"[{self._url}/rotate] response: {response.json()}")
        return response

    def __get_servo_angle(self):
        response = requests.get(f"{self._url}/get_servo_angle")
        LOGGER.info(f"[{self._url}/get_servo_angle] response: {response.json()}")
        j = response.json()
        if j is None or ("value" not in j):
            LOGGER.info("Remote SG90: Failed to get servo motor angle")
            return None
        return int(j["value"])

    def __check_alive(self):
        response = requests.get(f"{self._url}/check_alive", timeout=2)
        LOGGER.info(f"[{self._url}/check_alive] response: {response.json()}")
        return response.status_code == 200

    def __close(self):
        response = requests.get(f"{self._url}/close")
        LOGGER.info(f"[{self._url}/close] response: {response.json()}")
