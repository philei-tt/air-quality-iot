from flask import Flask, request, jsonify
from gpiozero import AngularServo
from gpiozero.pins.pigpio import PiGPIOFactory

from time import sleep

SERVO_CONTROL_PIN = 18
factory = PiGPIOFactory()
servo = AngularServo(SERVO_CONTROL_PIN, min_angle=0, max_angle=180, min_pulse_width=0.0005, max_pulse_width=0.0024, pin_factory=factory)

app = Flask(__name__)
PORT = 5000

servo_angle = 0

@app.route('/set_servo_angle', methods=['POST'])
def set_servo_angle():
    global servo_angle
    data = request.get_json()
    if not data or 'value' not in data:
        return jsonify({'status': 'error', 'message': 'No value provided'}), 400
    try:
        value = int(data['value'])
        if value < 0 or value > 180:
            raise ValueError()
    except ValueError:
        return jsonify({'status': 'error', 'message': 'Value is not valid integer in range [0:180]'}), 400
    print(f"Received set_servo_angle={servo_angle}")
    servo_angle = value
    servo.angle = servo_angle
    return jsonify({'status': 'success', 'new_value': servo_angle})

@app.route('/get_servo_angle', methods=['GET'])
def get_servo_angle():
    print(f"Received get_servo_angle")
    return jsonify({'value': servo_angle})

@app.route('/check_alive', methods=['GET'])
def check_alive():
    print("Alive")
    return jsonify({'alive': True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT)

