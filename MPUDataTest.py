from machine import Pin, I2C

MPU_ADDR = 0x68
i2c = I2C(0, scl=Pin(18), sda=Pin(19))
i2c.writeto(MPU_ADDR, bytes([107, 0]))

def read_word(h, l):
    value = h * 256 + l
    if value > 32767:
        value -= 65536
    return value

def get_all():
    d = i2c.readfrom_mem(MPU_ADDR, 0x3B, 14)

    ax = read_word(d[0], d[1]) // 1000
    ay = read_word(d[2], d[3]) // 1000
    az = read_word(d[4], d[5]) // 1000
    temp = read_word(d[6], d[7]) / 340 + 36.53
    gx = read_word(d[8], d[9]) // 1000
    gy = read_word(d[10], d[11]) // 1000
    gz = read_word(d[12], d[13]) // 1000

    return ax, ay, az, temp, gx, gy, gz
