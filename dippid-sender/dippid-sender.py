import socket
import time
import random
import numpy as np

IP = '127.0.0.1'
PORT = 5700

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

counter = 0

# https://medium.com/@thehippieandtheboss/how-to-create-random-numbers-in-python-3ddd1a0b2375
def create_button_input() -> str:
    random_button_press = random.randint(0, 1) #create random 0 or 1
    return '"button_1" : ' + str(random_button_press)

# https://numpy.org/doc/stable/reference/generated/numpy.sin.html#numpy.sin
def create_accelerometer_input() -> str:
    global counter
    counter += 0.1

    x = np.sin(counter)
    y = np.sin(counter * 3)
    z = np.sin(counter * 5)

    return '"accelerometer":{"x":' + str(x) + ',"y":' + str(y) + ',"z":' + str(z) + '}'

while True:
    button_message = create_button_input()
    accelerometer_message = create_accelerometer_input()
    message = '{' + button_message + ',' + accelerometer_message + '}'
    print(message)
    sock.sendto(message.encode(), (IP, PORT))
    time.sleep(1)
