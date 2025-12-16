from MPUDataTest import get_all

def gear_shift():
    ax, ay, az, temp, gx, gy, gz = get_all()

    if ax > 5:
        gear = 1
    elif ax > 2:
        gear = 2
    elif ax >= -5:
        gear = 3
    elif ax >= -8:
        gear = 4
    else:
        gear = 5

    return gear