# # We imports the GPIO module
# import RPi.GPIO as GPIO
# # We import the command sleep from time
# from time import sleep

# # Stops all warnings from appearing
# GPIO.setwarnings(False)

# # We name all the pins on BOARD mode
# GPIO.setmode(GPIO.BOARD)
# # Set an output for the PWM Signal
# GPIO.setup(18, GPIO.OUT)

# # Set up the PWM on pin #16 at 50Hz
# pwm = GPIO.PWM(18, 50)
# pwm.start(0) # Start the servo with 0 duty cycle ( at 0 deg position )
# while True:
#     try:
#         pwm.ChangeDutyCycle(5) # Tells the servo to turn to the left ( -90 deg position )
#         sleep(5) # Tells the servo to Delay for 5sec
#         pwm.ChangeDutyCycle(7.5) # Tells the servo to turn to the neutral position ( at 0 deg position )
#         sleep(5) # Tells the servo to Delay for 5sec
#         pwm.ChangeDutyCycle(10) # Tells the servo to turn to the right ( +90 deg position )
#         sleep(5) # Tells the servo to Delay for 5sec
#     except:
#         break
# pwm.stop(0) # Stop the servo with 0 duty cycle ( at 0 deg position )
# GPIO.cleanup() # Clean up all the ports we've used.

from gpiozero import AngularServo
from gpiozero.pins.pigpio import PiGPIOFactory

from time import sleep

singalPIN = 18
factory = PiGPIOFactory()

servo = AngularServo(singalPIN, min_angle=0, max_angle=180, min_pulse_width=0.0005, max_pulse_width=0.0024, pin_factory=factory)

while True:
    servo.angle = 0
    # sleep(1)
    input(">")
    servo.angle = 45
    # sleep(1)
    input(">")
    servo.angle = 90
    # sleep(1)
    input(">")
    servo.angle = 135
    # sleep(1)
    input(">")
    servo.angle = 180
    # sleep(1)
    input(">")
