# Air Quality System (AQS)
AQS is a simple yet effective example of home automation IoT project. 

# Idea / capabilities
The idea is to have one central microcontroller (Raspberry pi in this example) to measure air 
quality with different sensors, and more as actuators to control some device that can change 
those air quality indicators. 

Right now there are only 2 sensors (Temperature + Humidity (DHT-11)) and 1 actuator 
(Servo SG-90 to rotate humidifier intensity)

All nodes must be in the same wifi network, and actuators must host a HTTP server to modify state of actuators. 
Central node measure air quality and takes decision (as long as they are not too dificult to make 
on the edge). It is a client in respect to all the actuators. 

In addition, central node hosts a tiny BLE GATT server to configure it. 
Right now it notifies about current humidity and temperature, and allows to reconfigure target humidity and temperature

The project itends to be simple and flexible. 
- It should be easy to add new sensors, since all senors are hidden under same neat interface. 
- It should be easy to add new actuators, since they are also hidden under same abstraction
- Adding new reconfiguration paths for BLE reconfigurator is also simple 

# Things diagram
Here is a visualization of all the things (as of now) on the diagram:
![diagram](./media/AQS.png)

Central node (Pi5 b) hosts BLE GATT server with the following characterisics: 
- target temperature r/w
- target humidity r/w
- current temperature r/n (n - supports notification about current temperature)
- current humidity r/n

Central node is connected to the DHT11 and monitors temperature and humidity every 3 seconds. 
- current readings are logged to BLE GATT and Cloud logger to store in DynamoDB
- based on current readings, node makes decision if some actuators have to be adjusted. 
    - If humidity is higher / lower than target, -/+ rotation angle is sent via HTTP request to the servo actuator. Angle is propotional to difference between target and current. 

Cloud is AWS. 
- Communication is done throught IoT Core service via MQTT protocol. 
- IoT Core redirect message to the Lambda which parses it and stores data to noSQL DB (DynamoDB)

Actuator hosts Flask HTTP server with the following routes:
- `BASE_URL/rotate` - takes value (json {"value"; rotation_in_degrees})
- `BASE_URL/get_servo_angle` - returns value (json {"value": current_angle_in_degrees})
- `BASE_URL/check_alive` - returns status 200 if server alive
- `BASE_URL/close` - closes server

Servo SG90 is connected to the Xiaomi humidifier, with rotating dial (0 => 180 == OFF => max intensity)

# Code explanation
## Actuators/Sensors
Actuators and Sensors are hidden under a nice unified interfaces:
```python
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

class Actuator:
    def __init__(self, name):
        self._name = name
        
    def get_name(self):
        return self._name
    
    @abstractmethod
    def get_supported_actions(self) -> List[Action]:
        raise NotImplementedError()
    
    @abstractmethod
    def act(self, action: Action, value=None):
        raise NotImplementedError()
    
    @abstractmethod
    def get_state(self):
        raise NotImplementedError()
    
    @abstractmethod
    def is_alive(self):
        return True
    
    @abstractmethod
    def close(self):
        raise NotImplementedError()
```

This interface is same for DHT-11 temperature and humidity sensors, SG90, LED control and remote SG90 (used on central node, uses http requests to translate actions to actual actuator)

For DHT-11 `adafruit_dht` library is used to get readings.

For SG90 `gpiozero.AngularServo` + piGPIO is used to control SG90 via hardware PWM

## Server and client
Project assumes that all devices are in the same local network (basically connected to same WiFi). 

Actuators host simple `flask` server that enables central node to remotely control them. 

Server uses `requests` library to send HTTP requests and get responses. 

TODO:
- Currently actuators URLs are hardcoded, and they tend to change. AQS requires some automatic actuators discovery

## BLE reconfigurator
`bluezero` is used to setup simple GATT server so that user can configure AQS from the phone via "BLE Connector" or other app. 

## Services
Systemd services are setuped with `install_client.sh` and `install_server.sh` scripts, so that 
actuators and sensors start when raspberry is booted, and restart on failure. 

## Cloud
Logging to the cloud is done via `paho` library to properly use MQTT protocol. 

TODO: 
- right now cloud is setupped but ignores my messages for some reason. Investigate.

## LOGGER
All parts of AQS use same logger with nice formatting, that also supports logging to the file if needed. 
```bash
[DEB] [2025-02-19 21:52:30] [Debug message                                     ] [test.py:4]
[INF] [2025-02-19 21:52:30] [Info message                                      ] [test.py:5]
[WAR] [2025-02-19 21:52:30] [Warning message                                   ] [test.py:6]
[ERR] [2025-02-19 21:52:30] [Error message                                     ] [test.py:7]
[CRI] [2025-02-19 21:52:30] [Debug message                                     ] [test.py:8]
```

# Requirements
## Hardware
- Two Raspberry Pi4 (or newer)
- WiFi router / hotspot (Both Raspberries must be connected to same WiFi)
- DHT-11 sensor
- SG90 servo
- Few jumper wires


## Software
- Both Raspberries must be flashed with latest Raspberry Pi OS


# Setup + Usage
Install required packages:
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y libgpiod-dev gpiod
sudo systemctl enable --now pigpiod.service
```

Install required python libraries (I used root python environment for simplicity, you can switch to venv):
```bash
sudo pip3 install -r requirements.txt
```

Install and start services:
- Client: ```sudo ./install_client.sh```
- Server: ```sudo ./install_server.sh```