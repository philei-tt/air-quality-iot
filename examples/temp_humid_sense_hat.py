from sense_hat import SenseHat
from time import sleep
sense = SenseHat()

red = (255, 0, 0)
blue = (0, 0, 255)


while True:
    temp1 = sense.get_temperature_from_humidity()
    temp2 = sense.get_temperature_from_pressure()
    print(temp1, temp2)

    # pixels = [red if i < temp else blue for i in range(64)]
    # sense.set_pixels(pixels)
    # sense.show_message(str(round(temp)))
    sleep(1)
