from bluezero import peripheral
from bluezero import adapter
from bluezero import async_tools

from aqs.logger import LOGGER
from aqs.info import VERSION

# Define UUIDs for the service and characteristics
CONFIG_SERVICE_UUID = "0542"
# https://www.bluetooth.com/specifications/assigned-numbers/
TARGET_HUMIDITY_UUID = "2C0B"
TARGET_TEMP_UUID = "2B0D"
CURRENT_TEMP_UUID = "2A6E"
CURRENT_HUMIDITY_UUID = "2A6F"
CURRENT_TEMP_FMT_DSCP = "2904"


class BLEConfigurator:
    def __init__(
        self,
        device_name=f"AQS {VERSION}",
        notify_period_s: int = 1,
        target_humidity_rh: float = 50.00,
        target_temperature_C: float = 22.00,
        current_humidity_rh: float = -1.00,
        current_temperature_C: float = -1.00,
    ):
        self._device_name = device_name
        self._notify_period_s = notify_period_s

        # Initial target values
        self._target_humidity = target_humidity_rh
        self._target_temperature = target_temperature_C
        self._current_humidity = current_humidity_rh
        self._current_temperature = current_temperature_C

    # ------ Setter/Getter for current temperature / humidity ------ #
    def set_current_humidity(self, new_humidity: float):
        try:
            self._current_humidity = float(new_humidity)
        except Exception as e:
            LOGGER.error(f"Failed to set current humidity: {e}")

    def set_current_temperature(self, new_temperature: float):
        try:
            self._current_temperature = float(new_temperature)
        except Exception as e:
            LOGGER.error(f"Failed to set current temperature: {e}")
            
    def get_target_humidity(self):
        return self._target_humidity
    
    def get_target_temperature(self):
        return self._target_temperature

    # ------ Callbacks for GATT server ------ #
    def __read_target_humidity(self):
        LOGGER.info("Read request for target humidity")
        return bytes('%.2f' % self._target_humidity, "utf-8")

    def __write_target_humidity(self, value, options):
        try:
            self._target_humidity = float(value.decode("utf-8"))
            LOGGER.info(f"Updated target humidity to {self._target_humidity}")
        except Exception as e:
            LOGGER.error(f"Error updating target humidity: {e}")

    def __read_target_temp(self):
        LOGGER.info("Read request for target temperature")
        return bytes('%.2f' % self._target_temperature, "utf-8")

    def __write_target_temp(self, value, options):
        try:
            self._target_temperature = float(value.decode("utf-8"))
            LOGGER.info(f"Updated target temperature to {self._target_temperature}")
        except Exception as e:
            LOGGER.error(f"Error updating target temperature: {e}")

    def __read_current_temperature(self):
        LOGGER.info("Read request for current temperature")
        return bytes('%.2f' % self._current_temperature, "utf-8")

    def __read_current_humidity(self):
        LOGGER.info("Read request for current humidity")
        return bytes('%.2f' % self._current_humidity, "utf-8")

    def __update_current_temperature(self, characteristic):
        """
        Example of callback to send notifications

        :param characteristic:
        :return: boolean to indicate if timer should continue
        """
        # read/calculate new value.
        LOGGER.info("Update current temperature callaback")
        new_value = bytes('%.2f' % self._current_temperature, "utf-8")
        # Causes characteristic to be updated and send notification
        characteristic.set_value(new_value)
        # Return True to continue notifying. Return a False will stop notifications
        # Getting the value from the characteristic of if it is notifying
        return characteristic.is_notifying

    def __notify_current_temp_callback(self, notifying, characteristic):
        """
        Noitificaton callback example. In this case used to start a timer event
        which calls the update callback ever notify_period_s seconds

        :param notifying: boolean for start or stop of notifications
        :param characteristic: The python object for this characteristic
        """
        if notifying:
            async_tools.add_timer_seconds(
                self._notify_period_s,
                lambda ch: self.__update_current_temperature(ch),
                characteristic,
            )

    def __update_current_humidity(self, characteristic):
        """
        Example of callback to send notifications

        :param characteristic:
        :return: boolean to indicate if timer should continue
        """
        # read/calculate new value.
        LOGGER.info("Update current humidity callaback")
        new_value = bytes('%.2f' % self._current_humidity, "utf-8")
        # Causes characteristic to be updated and send notification
        characteristic.set_value(new_value)
        # Return True to continue notifying. Return a False will stop notifications
        # Getting the value from the characteristic of if it is notifying
        return characteristic.is_notifying

    def __notify_current_humidity_callback(self, notifying, characteristic):
        """
        Noitificaton callback example. In this case used to start a timer event
        which calls the update callback ever notify_period_s seconds

        :param notifying: boolean for start or stop of notifications
        :param characteristic: The python object for this characteristic
        """
        if notifying:
            async_tools.add_timer_seconds(
                self._notify_period_s,
                lambda ch: self.__update_current_humidity(ch),
                characteristic,
            )

    def run(self):
        # Create the peripheral (GATT server)
        device = peripheral.Peripheral(
            list(adapter.Adapter.available())[0].address,
            local_name=self._device_name,
            appearance=1344,
        )
        device.add_service(srv_id=1, uuid=CONFIG_SERVICE_UUID, primary=True)
        device.add_characteristic(
            srv_id=1,
            chr_id=1,
            uuid=TARGET_HUMIDITY_UUID,
            value=[],
            notifying=False,
            flags=["read", "write"],
            read_callback=lambda: self.__read_target_humidity(),
            write_callback=lambda v, o: self.__write_target_humidity(v, o),
            notify_callback=None,
        )

        device.add_characteristic(
            srv_id=1,
            chr_id=2,
            uuid=TARGET_TEMP_UUID,
            value=[],
            notifying=False,
            flags=["read", "write"],
            read_callback=lambda: self.__read_target_temp(),
            write_callback=lambda v, o: self.__write_target_temp(v, o),
            notify_callback=None,
        )

        device.add_characteristic(
            srv_id=1,
            chr_id=3,
            uuid=CURRENT_TEMP_UUID,
            value=[],
            notifying=True,
            flags=["read", "notify"],
            read_callback=lambda: self.__read_current_temperature(),
            write_callback=None,
            notify_callback=lambda n, c: self.__notify_current_temp_callback(n, c),
        )

        device.add_descriptor(
            srv_id=1,
            chr_id=3,
            dsc_id=1,
            uuid=CURRENT_TEMP_FMT_DSCP,
            value=[0x0E, 0xFE, 0x2F, 0x27, 0x01, 0x00, 0x00],
            flags=["read"],
        )

        device.add_characteristic(
            srv_id=1,
            chr_id=4,
            uuid=CURRENT_HUMIDITY_UUID,
            value=[],
            notifying=True,
            flags=["read", "notify"],
            read_callback=lambda: self.__read_current_humidity(),
            write_callback=None,
            notify_callback=lambda n, c: self.__notify_current_humidity_callback(n, c),
        )

        device.add_descriptor(
            srv_id=1,
            chr_id=4,
            dsc_id=1,
            uuid=CURRENT_TEMP_FMT_DSCP,
            value=[0x0E, 0xFE, 0x2F, 0x27, 0x01, 0x00, 0x00],
            flags=["read"],
        )

        print("Starting BLE GATT server...")
        device.publish()
