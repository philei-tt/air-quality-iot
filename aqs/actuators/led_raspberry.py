from gpiozero import LED

from aqs.actuators.actuator import Actuator, Action
from aqs.logger import LOGGER


class LEDActuator(Actuator):
    def __init__(self, name, pin=17):
        super().__init__(name)
        self._led = LED(pin)

    def get_supported_actions(self):
        return [Action.TURN_ON, Action.TURN_OFF, Action.BLINK]

    def act(self, action: Action, value=None):
        if action == Action.TURN_ON:
            self._led.on()
        elif action == Action.TURN_OFF:
            self._led.off()
        elif action == Action.BLINK:
            on_time = value // 2 if value is None else 1
            off_time = value // 2 if value is None else 1
            self._led.blink(on_time, off_time)
        else:
            LOGGER.error(f"[{self.get_name()}] [LED] Unsupported {action} action")
            return False
        return True

    def get_state(self):
        return self._led.is_active

    def close(self):
        self._led.close()
