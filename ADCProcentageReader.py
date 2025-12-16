from machine import ADC, Pin, I2C
import time
import struct
from ina219_clean import INA219


ADC_PIN = 34          
ADC_MAX = 4095        
VREF = 4.2            
DIVIDER_RATIO = 2     

BATTERY_MIN = 3.0    
BATTERY_MAX = 4.2     

# ---- SETUP ----
adc = ADC(Pin(ADC_PIN))
adc.atten(ADC.ATTN_11DB)  

i2c = I2C(0, scl=Pin(18), sda=Pin(19))
devices = i2c.scan()
print("devices:", devices)


class INA219:
    REG_CONFIG = 0x00
    REG_SHUNT_VOLTAGE = 0x01
    REG_BUS_VOLTAGE = 0x02
    REG_CALIBRATION = 0x05
    REG_CURRENT = 0x04
    REG_POWER = 0x03

    def __init__(self, i2c, addr=0x40, shunt_ohms=0.1):
        self.i2c = i2c
        self.addr = addr
        self.shunt_ohms = shunt_ohms

        
        config = 0x399F
        self._write_register(self.REG_CONFIG, config)

        
        self.current_lsb = 0.0001  
        cal = int(0.04096 / (self.current_lsb * shunt_ohms))
        self._write_register(self.REG_CALIBRATION, cal)

    def _write_register(self, reg, value):
        data = struct.pack('>H', value)
        self.i2c.writeto_mem(self.addr, reg, data)

    def _read_register(self, reg):
        data = self.i2c.readfrom_mem(self.addr, reg, 2)
        return struct.unpack('>h', data)[0]

    def bus_voltage(self):
        raw = self._read_register(self.REG_BUS_VOLTAGE)
        return (raw >> 3) * 0.004  

    def current(self):
        raw = self._read_register(self.REG_CURRENT)
        return raw * self.current_lsb * 1000  

    def power(self):
        raw = self._read_register(self.REG_POWER)
        return raw * self.current_lsb * 20 * 1000  
    

    
    def average_current(self, samples=20):
        total = 0
        for i in range(samples):
            total += self.current()
            time.sleep(0.05)
        return total / samples
    
    def threshhold_current(self):
        if self.current() > 40:
            return self.current
        else:
            return 2
        
    
    
BATTERY_CAPACITY_MAH = 2000
def remaining_time_hours(current_mA, percent):
    remaining_mAh = BATTERY_CAPACITY_MAH * (percent / 100)
    return remaining_mAh / max(current_mA, 1)


def read_battery_voltage():
    raw = adc.read()
    voltage = (raw / ADC_MAX) * VREF * DIVIDER_RATIO
    return voltage

def battery_percentage(voltage):
    percent = (voltage - BATTERY_MIN) / (BATTERY_MAX - BATTERY_MIN) * 100
    return max(0, min(100, percent))  

ina = INA219(i2c)



# ---- LOOP ----
def ADC_INA():
    
    vbat = read_battery_voltage()
    percent = battery_percentage(vbat)
    print(f'Battery raw ADC: {adc.read()}')
    print("Battery Voltage: {:.2f} V".format(vbat))
    print("Battery Level: {:.0f} %".format(percent))
    print("I2C devices:", devices)
    print("------v-INA-v-------------")
    
    
    
    voltage = ina.bus_voltage()
    current = ina.average_current()
    power = ina.power()
    
    print(hex(ina._read_register(INA219.REG_CONFIG)))
    print("Current (mA):", ina.average_current())
    print("Bus voltage:", ina.bus_voltage())
    
    LCDRemTime = remaining_time_hours(current, percent)
    
    print("Current: {:.1f} mA".format(current))
    
    print(f"Remaining time: {LCDRemTime}")
    print("-----v-GPIO-v--------")
    return LCDRemTime
    

