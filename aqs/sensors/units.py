from enum import Enum


class MeasurementUnit(Enum):
    TEMP_CELCIUM = 1
    HUMIDITY_RH = 2

    def __str__(self):
        match self:
            case MeasurementUnit.TEMP_CELCIUM:
                return 'C°'
            case MeasurementUnit.HUMIDITY_RH:
                return 'rH'
            case _:
                return '?'