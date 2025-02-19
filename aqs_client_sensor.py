# Client is the main piece of code. It has to:
# 1. Host a BLE GATT server to change target temp/humid, get reading from current temp/humid
# 2. Communicate with actuator over wifi HTTP Server
# 3. Take action (change humidity) or get it from the cloud
# 4. Log information to cloud


import threading
from aqs.logger import setup_logger, LOGGER
from aqs.argparser import parse_args
from aqs.ble_configurator import BLEConfigurator

from aqs.sensors.dht11_temperature import DHT11TemperatureSensor
from aqs.sensors.dht11_humidity import DHT11HumiditySensor

from aqs.actuators.remote_sg90 import RemoteSG90Actuator, Action

# from aqs.cloud_logger import AWSCloudMQQTLogger   # TODO: Fix cloud setup

from time import sleep
import requests

ACTUATOR_IP = "192.168.114.13"
ACTUATOR_PORT = 5000
ACTUATOR_URL = f"http://{ACTUATOR_IP}:{ACTUATOR_PORT}"
MEASURE_PERIOD_S = 3
Kp = 0.20 # TODO: adjust

counter = 0

def rotate_humidifier_intensity(config: BLEConfigurator, servo: RemoteSG90Actuator, current_humidity: float):
    # import random
    # servo.act(Action.ROTATE_DEG, )
    # if random.randint(0, 1):
    global counter
    
    error = config.get_target_humidity() - current_humidity  # positive error means humidity is low
    # Increase servo angle if humidity is too low, decrease if too high.
    # new_angle = servo.get_state() + Kp * error
    # new_angle = max(0, min(180, new_angle))
    angle_rotate = Kp * error
    servo.act(Action.ROTATE_DEG, angle_rotate)


def run_ble_server() -> BLEConfigurator:
    ble = BLEConfigurator()

    ble_thread = threading.Thread(target=lambda: ble.run())
    ble_thread.daemon = (
        True  # This makes sure the thread exits when the main program ends.
    )
    ble_thread.start()

    return ble


def check_servo_alive(servo: RemoteSG90Actuator):
    while True:
        try:
            if not remote_servo.is_alive():
                LOGGER.error("[Remote SG90] Server timeout")
                continue
            else:
                break
        except requests.exceptions.ConnectionError:
            LOGGER.error("[Remote SG90] Failed to connect to server")
            sleep(1)


if __name__ == "__main__":
    args = parse_args()
    setup_logger(args.loglevel, args.logfile)

    # configuration
    ble_config = run_ble_server()

    # sensors
    temp_sensor = DHT11TemperatureSensor("temp_sensor")
    humi_sensor = DHT11HumiditySensor("humi_sensor")

    # actuators
    remote_servo = RemoteSG90Actuator("remote_servo", ACTUATOR_URL)
    
    # Wait till connected
    check_servo_alive(remote_servo)

    temp_units_str = str(temp_sensor.get_units())
    humi_units_str = str(humi_sensor.get_units())

    while True:
        try:
            current_temp = temp_sensor.get_readings()
            current_humi = humi_sensor.get_readings()
            LOGGER.info(
                f"readings: (temp={current_temp} {temp_units_str}, humi={current_humi} {humi_units_str})"
            )

            ble_config.set_current_temperature(current_temp)
            ble_config.set_current_humidity(current_humi)
        except Exception as e:
            LOGGER.error(f"Measurement error: {e}")

        check_servo_alive(remote_servo)

        rotate_humidifier_intensity(ble_config, remote_servo, current_humi)


        sleep(MEASURE_PERIOD_S)
        # angle = input("Angle: ")
        # angle = int(angle)
        # set_servo_angle(angle)

        # get_servo_angle()
        # check_alive()
