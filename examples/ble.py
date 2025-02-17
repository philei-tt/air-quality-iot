from bluezero import peripheral
from bluezero import adapter

# Define UUIDs for the service and characteristics
CONFIG_SERVICE_UUID = "12345678-1234-5678-1234-56789abcdef0"
# TARGET_TEMP_UUID = "12345678-1234-5678-1234-56789abcdef2"
# TARGET_HUMIDITY_UUID = "12345678-1234-5678-1234-56789abcdef1"
# https://www.bluetooth.com/specifications/assigned-numbers/ 
TARGET_TEMP_UUID = "0x0543" 
TARGET_HUMIDITY_UUID = "0x0544"

# Initial target values
target_humidity = 50
target_temperature = 22


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

    print("Starting BLE GATT server...")
    device.publish()
