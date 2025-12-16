from uthingsboard.client import TBDeviceMqttClient
from time import sleep
from machine import reset, UART
from machine import Pin, ADC, I2C
import gc
import secrets
from gps_simple import GPS_SIMPLE
import MPUDataTest
import MPUReceiveTest
from SpeedStuff import speed
from LCDDisplay import update_lcd
from Gear import gear_shift
from DirectionStuff import direction
from Brakey import update_brakelight
from ADCProcentageReader import INA219
from ADCProcentageReader import ADC_INA
import ina219_clean
import struct

from umqtt.simple import MQTTClient
import json


pb1 = Pin(4,Pin.IN)

counter = 0
stopped_sent = False
prev_lat_lon = None
bike_moving = True
bike_stopped = False
bike_stolen = False
stop_time = 7
spd = 0

HA_stolen = 0
HA_help = 0
gps_port = 2                       
gps_speed = 9600                           
uart = UART(gps_port, gps_speed)           
gps = GPS_SIMPLE(uart)                     
def get_lat_lon():
    lat = lon = None                       
    if gps.receive_nmea_data():            
                                          
        if gps.get_latitude() != -999.0 and gps.get_longitude() != -999.0 and gps.get_validity() == "A":
            lat = str(gps.get_latitude())  
            lon = str(gps.get_longitude()) 
            return lat, lon                
        else:                              
            print(f"GPS data to server not valid:\nlatitude: {lat}\nlongtitude: {lon}")
            return False
    else:
        return False
                                           
client = TBDeviceMqttClient(secrets.SERVER_IP_ADDRESS, access_token = secrets.ACCESS_TOKEN)
client.connect()                           
print("connected to thingsboard, starting to send and receive data")

mqtt = MQTTClient(
    b"educaa",
    secrets.HA_MQTT_IP,
    secrets.HA_MQTT_PORT,
    user=secrets.HA_MQTT_USER,
    password=secrets.HA_MQTT_PASSWORD
    )

mqtt.connect()
while True:
    try:
        print(f"free memory: {gc.mem_free()}") 
        
        if gc.mem_free() < 2000:          
            print("Garbage collected!")
            gc.collect()                 
        
        lat_lon = get_lat_lon()
        if lat_lon:
            client.send_telemetry({'latitude': lat_lon[0], 'longitude': lat_lon[1]})
            json_payload_lat=json.dumps(float(lat_lon[0]))
            mqtt.publish("Lat",json_payload_lat)
            json_payload_lon=json.dumps(float(lat_lon[1]))
            mqtt.publish("Lon",json_payload_lon)
            
            
            if pb1.value() == 0:
                bike_moving = True
                bike_stopped = False
                bike_stolen = False
                stopped_sent = False
                counter = 0
            else:
                if prev_lat_lon is None:
                    prev_lat_lon = lat_lon

                if lat_lon == prev_lat_lon:
                    counter += 1
                    if counter >= stop_time:
                        bike_stopped = True
                        bike_moving = False
                        stopped_sent = True
                    else:
                        bike_moving = True
                        bike_stopped = False
                else:
                    if stopped_sent and counter >= stop_time:
                        bike_stolen = True
                    bike_moving = True
                    bike_stopped = False
                    stopped_sent = False
                    counter = 0
                    prev_lat_lon = lat_lon
                
                if bike_stolen == True:
                    HA_stolen = 1
                else:
                    HA_stolen = 0
                json_payload_stolen=json.dumps(HA_stolen)
                mqtt.publish("Stolen",json_payload_stolen)

            client.send_telemetry({
                'bike_moving': bike_moving,
                'bike_stopped': bike_stopped,
                'bike_stolen': bike_stolen
            
            
            
            })
            
            print("Counter:", counter)
            print("button: ",pb1.value())
            print("bike_moving:", bike_moving)
            print("bike_stopped:", bike_stopped)
            print("bike_stolen:", bike_stolen)
        
        update_brakelight()
        
        mpu_data = MPUDataTest.get_all()
        if mpu_data:
            ax, ay, az, temp, gx, gy, gz = mpu_data
            imustats = {
                'ax': ax,
                'ay': ay,
                'az': az,
                'temp': round(temp, 1),
                'gx': gx,
                'gy': gy,
                'gz': gz
            }
            client.send_telemetry(imustats) 
            print("IMU sent:", imustats)
            json_payload=json.dumps(temp)
            mqtt.publish("temp",json_payload)
            json_payload_ay=json.dumps(ay)
            mqtt.publish("ay",json_payload_ay)
            json_payload_ax=json.dumps(ax)
            mqtt.publish("ax",json_payload_ax)
        
        MPUReceiveTest.update_alarm()

        if MPUReceiveTest.send_help:
            print("Sending HELP to ThingsBoard!")
            client.send_telemetry({"help": True})
            sleep(0.1)
            client.send_telemetry({"help": False})
         
        update_brakelight() 
        
        if MPUReceiveTest.send_help == True:
            HA_help = 1
        else:
            HA_help = 0

        json_payload_Help = json.dumps(HA_help)
        mqtt.publish("Help", json_payload_Help)
        MPUReceiveTest.send_help = False
        
        update_brakelight()

        if lat_lon:
            spd = speed(lat_lon[0], lat_lon[1])
            client.send_telemetry({"speed": round(spd, 1)})
            print("Speed:", round(spd, 1))

            dir = direction(lat_lon[0], lat_lon[1])
            client.send_telemetry({"direction": dir})
            print("Direction:", dir)



        gear = gear_shift()
        RemTime = ADC_INA()

        client.send_telemetry({"RemTime": RemTime})
        json_payload_RemTime = json.dumps(RemTime)
        mqtt.publish("RemTime", json_payload_RemTime)

        update_brakelight()

        update_lcd(spd, temp, gear, RemTime)
        
        sleep(0.5)
        
        
    except KeyboardInterrupt:
        print("Disconnected!")
        client.disconnect()               
        reset()                          