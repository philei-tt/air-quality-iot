from dataclasses import dataclass
from enum import Enum
from typing import List, Dict
import json

import ssl  # For handling SSL/TLS encryption
import paho.mqtt.client as mqtt  # For MQTT communication

from aqs.sensors.units import MeasurementUnit
from aqs.logger import LOGGER

CERT_FILE = "client-certificate.pem.crt"
KEY_FILE = "client-private.pem.key"
ROOT_CA_FILE = "AmazonRootCA1.pem"


# Supported things
class SensorType(Enum):
    DHT_11_TEMPERATURE = 0
    DHT_11_HUMIDITY = 1


SENSOR_UNITS = {
    SensorType.DHT_11_TEMPERATURE: MeasurementUnit.TEMP_CELCIUM,
    SensorType.DHT_11_HUMIDITY: MeasurementUnit.HUMIDITY_RH,
}

SENSORS_MEASUREMENT = {
    SensorType.DHT_11_TEMPERATURE: "temperature",
    SensorType.DHT_11_HUMIDITY: "humidity",
}


@dataclass
class SensorConfiguration:
    thing_name: str  # !!! Must be unique
    sensor_type: SensorType


class AWSCloudMQQTLogger:
    def __init__(
        self,
        aws_endpoint: str,
        sensors_configs: List[SensorConfiguration],
        tprotocol: str,
    ):
        self.clients = {}
        self.configs: Dict[str, SensorConfiguration] = {}
        # Open client for each thing:
        for conf in sensors_configs:
            thing_name = conf.thing_name
            self.configs[thing_name] = conf
            client = mqtt.Client(
                mqtt.CallbackAPIVersion.VERSION2,
                client_id=thing_name,
                transport=tprotocol,
                protocol=mqtt.MQTTv5,
            )
            client.tls_set(
                ROOT_CA_FILE,
                certfile=CERT_FILE,
                keyfile=KEY_FILE,
                cert_reqs=ssl.CERT_REQUIRED,
                tls_version=ssl.PROTOCOL_TLSv1_2,
                ciphers=None,
            )
            client.on_message = self.on_message
            # Connect to AWS IoT Core
            if tprotocol == "tcp":
                mport = 8883
            else:
                mport = 443
            client.connect(aws_endpoint, mport)

            # Start the MQTT client loop
            client.loop_start()

            # Subscribe to all topics related to the device and its shadows. QoS is set to 2
            client.subscribe(f"$aws/things/{thing_name}/shadow/update/accepted")
            client.subscribe(f"$aws/things/{thing_name}/shadow/update/rejected")

            self.clients[thing_name] = client

    def log(self, thing_name, value):
        if thing_name not in self.configs:
            LOGGER.error(f"Tried to log unknown thing: {thing_name}")
            return

        self.clients[thing_name].publish(
            f"$aws/things/{thing_name}/shadow/update",
            json.dumps(
                {
                    "state": {
                        "reported": {
                            str(
                                SENSORS_MEASUREMENT[
                                    self.configs[thing_name].sensor_type
                                ]
                            ): value,
                            "units": str(
                                SENSOR_UNITS[self.configs[thing_name].sensor_type]
                            ),
                            "thingid": thing_name,
                            "source": thing_name,
                        }
                    }
                }
            ),
        )

    @staticmethod
    def on_message(client, userdata, message):
        # Decode the incoming message payload
        string_message = str(message.payload.decode())

        # Handle messages on delta topic
        # print(f"Received message on topic {message.topic}: {string_message}")
        if "accepted" in message.topic:
            decoded_message = json.loads(message.payload.decode())

            # Update desired temperature
            if "status" in string_message:
                status = decoded_message["state"]["status"]
                LOGGER.info(f"Response status from cloud: {status}")
            else:
                LOGGER.warning("Reponse from cloud doesn't have status")

        if "rejected" in message.topic:
            decoded_message = json.loads(message.payload.decode())

            # Update desired temperature
            if "reason" in string_message:
                reason = decoded_message["state"]["reason"]
                LOGGER.error(f"Cloud rejected message, reason: {reason}")
            else:
                LOGGER.error(f"Cloud rejected message")
