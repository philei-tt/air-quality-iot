import requests

SERVER_IP = '192.168.135.13'
PORT = 5000
BASE_URL = f'http://{SERVER_IP}:{PORT}'

def set_servo_angle(value):
    response = requests.post(f'{BASE_URL}/set_servo_angle', json={'value': value})
    print('set_value response:', response.json())

def get_servo_angle():
    response = requests.get(f'{BASE_URL}/get_servo_angle')
    print('get_value response:', response.json())

def check_alive():
    response = requests.get(f'{BASE_URL}/check_alive')
    print('check_alive response:', response.json())

if __name__ == '__main__':
    while True:
        angle = input("Angle: ")
        angle = int(angle)
        set_servo_angle(angle)
        
        get_servo_angle()
        check_alive()
