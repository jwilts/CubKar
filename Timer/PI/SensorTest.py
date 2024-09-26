#!/usr/bin/env python
import time 
import RPi.GPIO as GPIO

#set input gpio pin numbers 
LaneOne = 36 
LaneTwo = 38
LaneThree = 40
PadSwitch = 32
StartSwitch = 29
## Set Bounce Time for inputs
Btime = 100


GPIO.setwarnings(False)
GPIO.setmode (GPIO.BOARD)
GPIO.setup(LaneOne,GPIO.IN,pull_up_down = GPIO.PUD_UP)
GPIO.setup(LaneTwo,GPIO.IN,pull_up_down = GPIO.PUD_UP)
GPIO.setup(LaneThree,GPIO.IN,pull_up_down = GPIO.PUD_UP)
GPIO.setup(PadSwitch,GPIO.IN,pull_up_down = GPIO.PUD_UP)
GPIO.setup(StartSwitch,GPIO.IN, pull_up_down = GPIO.PUD_UP)

# set output led gpio pin numbers
leds = [16,18,7,11,13,15,8,10,12]
# leds = [3,5,7,11,13,15,8,10,12]


x = 0
while x < 9:
   GPIO.setup(leds[x],GPIO.OUT)
   GPIO.output(leds[x],GPIO.HIGH)
   x +=1

time.sleep(int(3))

x = 0
while x < 9:
   GPIO.setup(leds[x],GPIO.OUT)
   GPIO.output(leds[x],GPIO.LOW)
   x +=1

x = 0
GPIO.add_event_detect(LaneOne, GPIO.RISING, bouncetime = Btime)
GPIO.add_event_detect(LaneTwo, GPIO.RISING, bouncetime = Btime)
GPIO.add_event_detect(LaneThree, GPIO.RISING, bouncetime = Btime)
GPIO.add_event_detect(PadSwitch, GPIO.RISING, bouncetime = Btime)
GPIO.add_event_detect(StartSwitch, GPIO.RISING, bouncetime = Btime)
   
while True:
	x +=1
	
	if GPIO.event_detected( LaneOne ):	
		Msg = str(x) + " Lane 1"
		print (Msg)

	if GPIO.event_detected( LaneTwo ):	
		Msg = str(x) + " Lane 2"
		print (Msg)

	if GPIO.event_detected( LaneThree ):	
		Msg = str(x) + " Lane 3"
		print (Msg)

	if GPIO.event_detected( StartSwitch ):	
		Msg = str(x) + " Start Switch"
		print (Msg)
	
    
	if GPIO.event_detected( PadSwitch ):	
		Msg = str(x) + " Pad Switch"
		print (Msg)
				
	## time.sleep(int(1))
   
   