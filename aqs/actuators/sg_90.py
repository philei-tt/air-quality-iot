from gpiozero import AngularServo
from gpiozero.pins.pigpio import PiGPIOFactory
from time import sleep

from aqs.actuators.actuator import Actuator, Action
from aqs.logger import LOGGER


class SG90Actuator(Actuator):
    def __init__(self, name, control_pin=18):
        super().__init__(name)
        self._factory = PiGPIOFactory()
        self._servo = AngularServo(
            control_pin,
            min_angle=0,
            max_angle=180,
            min_pulse_width=0.0005,
            max_pulse_width=0.0024,
            pin_factory=self._factory,
        )

        # Start sequence (0->180->0)
        self._servo.angle = 0
        sleep(2)
        self._servo.angle = 180
        sleep(2)
        self._servo.angle = 0

    def get_supported_actions(self):
        return [Action.ROTATE]

    def act(self, action: Action, value):
        if action != Action.ROTATE:
            LOGGER.error(f"[{self.get_name()}] [SG90] Unsupported {action} action")
            return
        try:
            new_angle = self._servo.angle + int(value)
            if (
                new_angle < self._servo.min_angle()
                or new_angle > self._servo.max_angle()
            ):
                incorrent_angle = new_angle
                new_angle = min(
                    self._servo.max_angle(), max(self._servo.min_angle(), new_angle)
                )
                LOGGER.warning(
                    f"[{self.get_name()}] [SG90] Angle is too big/small: {incorrent_angle}, defaulting to {new_angle}"
                )
            self._servo.angle = new_angle
        except Exception as e:
            LOGGER.error(f"[{self.get_name()}] [SG90] Action fail: {e}")

    def get_state(self):
        return self._servo.angle

    def close(self):
        self._servo.close()
        raise NotImplementedError()
