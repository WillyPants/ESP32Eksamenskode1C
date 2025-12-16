from neopixel import NeoPixel
from machine import Pin
from MPUDataTest import get_all

ANTAL = 12
np = NeoPixel(Pin(12, Pin.OUT), ANTAL)

prev_ax = None
THRESHOLD = -5

def clear():
    for i in range(ANTAL):
        np[i] = (0, 0, 0)
    np.write()

def brake_on():
    for i in range(ANTAL):
        np[i] = (255, 0, 0)
    np.write()

def update_brakelight():
    global prev_ax

    ax, ay, az, temp, gx, gy, gz = get_all()

    if prev_ax is not None:
        if ax - prev_ax < THRESHOLD:
            brake_on()
        else:
            clear()

    prev_ax = ax