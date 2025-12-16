import math

prev_lat = None
prev_lon = None

def speed(lat, lon):
    global prev_lat, prev_lon
    lat, lon = float(lat), float(lon)
    
    if prev_lat is None:
        prev_lat, prev_lon = lat, lon
        return 0

    dist = ((lat - prev_lat)**2 + (lon - prev_lon)**2)**0.5 * 111000
    prev_lat, prev_lon = lat, lon

    return dist * 3.6