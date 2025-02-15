import requests

SERVER_IP = 'SERVER_IP_ADDRESS'
PORT = 5000
BASE_URL = f'http://{SERVER_IP}:{PORT}'

def set_value(value):
    response = requests.post(f'{BASE_URL}/set_value', json={'value': value})
    print('set_value response:', response.json())

def get_value():
    response = requests.get(f'{BASE_URL}/get_value')
    print('get_value response:', response.json())

def check_alive():
    response = requests.get(f'{BASE_URL}/check_alive')
    print('check_alive response:', response.json())

if __name__ == '__main__':
    while True:
        angle = input("Angle: ")
        angle = int(angle)
        set_value(angle)
        
        get_value()
        check_alive()