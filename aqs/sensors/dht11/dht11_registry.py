import adafruit_dht

__SENSORS_MAP = None

def get_dht11_sensor(data_pin):
    global __SENSORS_MAP
    
    if __SENSORS_MAP is None:
        __SENSORS_MAP = {id(data_pin): adafruit_dht.DHT11(data_pin)}
    
    if id(data_pin) not in __SENSORS_MAP:
        __SENSORS_MAP[id(data_pin)] = adafruit_dht.DHT11(data_pin)
    
    return __SENSORS_MAP[id(data_pin)]