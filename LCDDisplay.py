from gpio_lcd import GpioLcd
from machine import Pin
from Gear import gear_shift

lcd = GpioLcd(rs_pin=Pin(27), enable_pin=Pin(25),
              d4_pin=Pin(33), d5_pin=Pin(32),
              d6_pin=Pin(21), d7_pin=Pin(22),
              num_lines=4, num_columns=20)

custom_chr = bytearray([
    0b01110,
    0b01010,
    0b01110,
    0b00000,
    0b00000,
    0b00000,
    0b00000,
    0b00000
])

def update_lcd(speed, temp, gear, RemTime):
    gear = gear_shift()
    lcd.custom_char(0, custom_chr)
    lcd.clear()
    lcd.move_to(0,0)
    lcd.putstr(f"{round(speed)} km/t       {gear}. Gear")
    lcd.move_to(0,1)
    lcd.putstr(f"{round(temp)}")
    lcd.putchar(chr(0))
    lcd.putstr("C")
    lcd.move_to(0,2)
    lcd.putstr(f"Remaining time: {RemTime}")
    