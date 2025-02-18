from flask import Flask, request, jsonify

from aqs.actuators.sg_90 import SG90Actuator, Action
from aqs.logger import LOGGER, setup_logger
from aqs.argparser import parse_args

servo = SG90Actuator("servo", 18)

app = Flask(__name__)
PORT = 5000

@app.route("/rotate", methods=["POST"])
def set_servo_angle():
    global servo
    
    data = request.get_json()
    if not data or "value" not in data:
        return jsonify({"status": "error", "message": "No value provided"}), 400
    rotate_deg = 0
    try:
        rotate_deg = float(data["value"])
        rotated = servo.act(Action.ROTATE_DEG, rotate_deg)
        if not rotated:
            raise RuntimeError("Failed to rotate")
    except Exception as e:
        LOGGER.error(f"Error rotating: {e}")
        return jsonify({"status": "error", "message": str(e)}), 400
    LOGGER.info(f"Successfully rotated by {rotate_deg}")
    return jsonify({"status": "success", "new_value": servo.get_state()})

@app.route("/get_servo_angle", methods=["GET"])
def get_servo_angle():
    LOGGER.info(f"Received get_servo_angle")
    return jsonify({"value": servo.get_state()})

@app.route("/check_alive", methods=["GET"])
def check_alive():
    LOGGER.info("Received check_alive")
    return jsonify({"alive": True})

@app.route("/close", methods=["GET"])
def close():
    LOGGER.info("Received close")
    return jsonify({"close": True})


if __name__ == "__main__":
    args = parse_args()
    setup_logger(args.loglevel, args.logfile)

    app.run(host="0.0.0.0", port=PORT)

