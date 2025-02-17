from abc import abstractmethod


class Sensor:
    def __init__(self, name):
        self._name = name

    def get_name(self):
        return self._name

    @abstractmethod
    def get_units(self):
        raise NotImplementedError()

    @abstractmethod
    def get_readings(self):
        raise NotImplementedError()

    @abstractmethod
    def close(self):
        raise NotImplementedError()
