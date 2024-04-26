from DIPPID import SensorUDP

# use UPD (via WiFi) for communication
PORT = 5700
sensor = SensorUDP(PORT)

def handle_button_1(data):
    print("button_1: " + str(data))

def handle_accelerometer(data):
    print("accelerometer_x:" + str(data.get("x")))
    print("accelerometer_y:" + str(data.get("y")))
    print("accelerometer_z:" + str(data.get("z")))

sensor.register_callback('button_1', handle_button_1)
sensor.register_callback('accelerometer', handle_accelerometer)