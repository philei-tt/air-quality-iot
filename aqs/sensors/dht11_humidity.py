# Complete Project Details: https://RandomNerdTutorials.com/raspberry-pi-dht11-dht22-python/
# Based on Adafruit_CircuitPython_DHT Library Example

import board

from aqs.sensors.sensor import Sensor
from aqs.sensors.units import MeasurementUnit
from aqs.logger import LOGGER
from aqs.sensors.dht11.dht11_registry import get_dht11_sensor


class DHT11HumiditySensor(Sensor):
    def __init__(self, name, data_pin=board.D4):
        super().__init__(name)
        self._sensor = get_dht11_sensor(data_pin)

    def get_units(self):
        return MeasurementUnit.HUMIDITY_RH

    def get_readings(self):
        readings = self._sensor.humidity
        LOGGER.debug(f"[DHT11-humid] [{self.get_name()}] get readings: {readings}")
        return readings

    def close(self):
        self._sensor.exit()
