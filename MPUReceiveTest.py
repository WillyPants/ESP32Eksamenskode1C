from machine import Pin, PWM
from time import sleep
from MPUDataTest import get_all

buzzer = PWM(Pin(14, Pin.OUT), duty=0)
pb1 = Pin(4,Pin.IN)

alarm_on = False
send_help = False
cancel_alarm = False
countdown_active = False
timetostop = 7
countdown = timetostop


def play_tone(freq=220, tone_dur=0.3, sil_dur=0):
    buzzer.duty(512)
    buzzer.freq(freq)
    sleep(tone_dur)
    buzzer.duty(0)
    sleep(sil_dur)

def update_alarm():
    global alarm_on, send_help, cancel_alarm, countdown_active, countdown

    if alarm_on and countdown_active:
        if pb1.value() ==0:
            cancel_alarm = True
        if cancel_alarm:
            alarm_on = False
            countdown_active = False
            countdown = timetostop
            send_help = False
            print("Alarm Cancelled")
            return

        play_tone()
        print("Sending help in", countdown, "seconds...")
        countdown -= 1

        if countdown <= 0:
            send_help = True
            alarm_on = False
            countdown_active = False
        return

    ax, ay, az, temp, gx, gy, gz = get_all()

    if (ay >= 12 or ay <= -12) and not alarm_on:
        print("ALARM TRIGGERED!")
        cancel_alarm = False
        alarm_on = True
        countdown_active = True
        countdown = timetostop
        