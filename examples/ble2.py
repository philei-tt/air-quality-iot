from bluezero import peripheral
from bluezero import adapter
from bluezero import async_tools

# Define UUIDs for the service and characteristics
# CONFIG_SERVICE_UUID = "12345678-1234-5678-1234-56789abcdef0"
CONFIG_SERVICE_UUID = "0542"
# TARGET_HUMIDITY_UUID = "12345678-1234-5678-1234-56789abcdef1"
# TARGET_TEMP_UUID = "12345678-1234-5678-1234-56789abcdef2"
# https://www.bluetooth.com/specifications/assigned-numbers/ 
TARGET_HUMIDITY_UUID = "2A6F"
TARGET_TEMP_UUID = "2B11"
CURRENT_TEMP_UUID = "2A6E"
CURRENT_TEMP_FMT_DSCP = '2904'

# Initial target values
target_humidity = 50
target_temperature = 22

current_humidity = 32
current_temperature = 25


def read_target_humidity():
    print("Read request for target humidity")
    return bytes(str(target_humidity), "utf-8")


def write_target_humidity(value, options):
    global target_humidity
    try:
        target_humidity = int(value.decode("utf-8"))
        print("Updated target humidity to", target_humidity)
    except Exception as e:
        print("Error updating target humidity:", e)


def read_target_temp():
    print("Read request for target temperature")
    return bytes(str(target_temperature), "utf-8")


def write_target_temp(value, options):
    global target_temperature
    try:
        target_temperature = int(value.decode("utf-8"))
        print("Updated target temperature to", target_temperature)
    except Exception as e:
        print("Error updating target temperature:", e)
        
def read_current_temp():
    print("Read request for current temperature")
    return bytes(str(current_temperature), "utf-8")


def update_current_temp(characteristic):
    """
    Example of callback to send notifications

    :param characteristic:
    :return: boolean to indicate if timer should continue
    """
    # read/calculate new value.
    print("Update callaback")
    global current_temperature
    current_temperature += 1
    new_value = bytes(str(current_temperature), "utf-8")
    # Causes characteristic to be updated and send notification
    characteristic.set_value(new_value)
    # Return True to continue notifying. Return a False will stop notifications
    # Getting the value from the characteristic of if it is notifying
    return characteristic.is_notifying

def notify_current_temp_callback(notifying, characteristic):
    """
    Noitificaton callback example. In this case used to start a timer event
    which calls the update callback ever 1 seconds

    :param notifying: boolean for start or stop of notifications
    :param characteristic: The python object for this characteristic
    """
    if notifying:
        async_tools.add_timer_seconds(1, update_current_temp, characteristic) 

if __name__ == "__main__":
    # Create the peripheral (GATT server)
    device = peripheral.Peripheral(
        list(adapter.Adapter.available())[0].address,
        local_name="PiConfigBLE",
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
        read_callback=read_target_humidity,
        write_callback=write_target_humidity,
        notify_callback=None,
    )

    device.add_characteristic(
        srv_id=1,
        chr_id=2,
        uuid=TARGET_TEMP_UUID,
        value=[],
        notifying=False,
        flags=["read", "write"],
        read_callback=read_target_temp,
        write_callback=write_target_temp,
        notify_callback=None,
    )
    
    device.add_characteristic(
        srv_id=1,
        chr_id=3,
        uuid=CURRENT_TEMP_UUID,
        value=[],
        notifying=True,
        flags=["read", "notify"],
        read_callback=read_current_temp,
        write_callback=None,
        notify_callback=notify_current_temp_callback,
    )
    
    device.add_descriptor(srv_id=1, chr_id=3, dsc_id=1, uuid=CURRENT_TEMP_FMT_DSCP,
                               value=[0x0E, 0xFE, 0x2F, 0x27, 0x01, 0x00,
                                      0x00],
                               flags=['read'])



    print("Starting BLE GATT server...")
    device.publish()
