#!/usr/bin/env python
import time 
import RPi.GPIO as GPIO

#set input gpio pin numbers 
LaneOne = 16 
LaneTwo = 18
LaneThree = 22


max_race_time = 20 # in seconds, times out after this time

GPIO.setwarnings(False)
GPIO.setmode (GPIO.BOARD)
GPIO.setup(LaneOne,GPIO.IN,pull_up_down = GPIO.PUD_UP)
GPIO.setup(LaneTwo,GPIO.IN,pull_up_down = GPIO.PUD_UP)
GPIO.setup(LaneThree,GPIO.IN,pull_up_down = GPIO.PUD_UP)

# set output led gpio pin numbers
leds = [3,5,21,11,13,15,8,10,12]

# turn LED's off
x = 0
while x < 9:
    GPIO.setup(leds[x],GPIO.OUT)
    GPIO.output(leds[x],GPIO.LOW)
    x +=1
    
# Run test cycle of the LEDs
x = 0
while x < 9:
    GPIO.setup(leds[x],GPIO.OUT)

    GPIO.output(leds[x],GPIO.HIGH)
    time.sleep(0.2)
    # GPIO.output(leds[x],GPIO.LOW)
    x +=1
time.sleep(2)
x = 0

# Turn LED's Off
while x < 9:
    GPIO.setup(leds[x],GPIO.OUT)
    GPIO.output(leds[x],GPIO.LOW)
    x +=1
