prev_lat_dir = None
prev_lon_dir = None

def direction(lat, lon):
    global prev_lat_dir, prev_lon_dir
    lat = float(lat)
    lon = float(lon)

    if prev_lat_dir is None:
        prev_lat_dir = lat
        prev_lon_dir = lon
        return ""

    dlat = lat - prev_lat_dir
    dlon = lon - prev_lon_dir

    prev_lat_dir = lat
    prev_lon_dir = lon

    if abs(dlat) > abs(dlon):
        return "N" if dlat > 0 else "S"
    else:
        return "E" if dlon > 0 else "W"