#!/usr/bin/env python
import time 
import RPi.GPIO as GPIO
from Tkinter import *
import tkFont
import ConfigParser
import os
import logging

############################################################################################################
## load 8x8 matrix info
############################################################################################################
import re
import argparse
from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.core.virtual import viewport
from luma.core.legacy import text, show_message
from luma.core.legacy.font import proportional, CP437_FONT, TINY_FONT, SINCLAIR_FONT, LCD_FONT

## Turn on the debugger if the program is being stupid.
# import pdb; pdb.set_trace()

# from threading import Thread

############################################################################################################
	
##  ------  Function Definitions
############################################################################################################
## Create a config file
############################################################################################################
def create_config(path):
	config = ConfigParser.ConfigParser()
	config.add_section("Settings")
	config.set("Settings", "max_race_time", "")
	config.set("Settings", "min_race_time", "")
	config.set("Settings", "switch_bounce_time", "")
	config.set("Settings", "GPIOLane1", "")
	config.set("Settings", "GPIOLane2", "")
	config.set("Settings", "GPIOLane3", "")
	config.set("Settings", "GPIOSwitch","")
	config.set("Settings", "GPIOBounce_time","")
	config.set("settings", "Leds","")
	config.set("settings", "Unit","")
	config.set("settings", "MatrixYN","")
	config.set("Races", "GFastestLane", "")
	config.set("Races", "GFastestTime", "")
	config.set("Races", "GFastestRaceCounter", "")	
	config.set("Races", "race_counter","")
	with open(path, "wb") as config_file:
		config.write(config_file)
		
############################################################################################################		
## Return a Config object		
############################################################################################################
def get_config(path):
	if not os.path.exists(path):
		create_config(path)
	config = ConfigParser.ConfigParser()
	config.read(path)
	return config

############################################################################################################	
## Return a Setting and Optionally Print to screen for debugging purposes	
############################################################################################################
def get_setting(path, section, setting, diplay):
    config = get_config(path)
    value = config.get(section, setting)
    if diplay == True:
        print "{section} {setting} is {value}".format(
            section=section, setting=setting, value=value)
    return value

############################################################################################################	
## Read an Array delimited by commas	
############################################################################################################
def get_setting2(path, section, setting, diplay):
    config = get_config(path)
    value = config.get(section, setting).split(',')
	
    if diplay == True:
        print "{section} {setting} is {value}".format(
            section=section, setting=setting, value=value)
    return value
	
############################################################################################################	
## Update a Setting	
############################################################################################################
def update_setting(path, section, setting, value):
    config = get_config(path)
    config.set(section, setting, value)
    with open(path, "wb") as config_file:
        config.write(config_file)
############################################################################################################
## Delete a Setting
############################################################################################################
def delete_setting(path, section, setting):
    config = get_config(path)
    config.remove_option(section, setting)
    with open(path, "wb") as config_file:
        config.write(config_file)

############################################################################################################
# Reset LED's to an off state
############################################################################################################
def resetLEDS():
	x = 0
	while x < 9:
		GPIO.setup(leds[x],GPIO.OUT)
		GPIO.output(leds[x],GPIO.LOW)
		x +=1
		
############################################################################################################		
# Run test cycle of the LEDs
############################################################################################################
def testLEDS():
	x = 0
	while x < 9:
		GPIO.setup(leds[x],GPIO.OUT)
		GPIO.output(leds[x],GPIO.HIGH)
		time.sleep(0.1)
		GPIO.output(leds[x],GPIO.LOW)
		x +=1

############################################################################################################		
# 3 quick flashes of the LEDS		
############################################################################################################
def flashLEDS() :
	
	x = 0
	y = 0
	while y < 3:
		while x < 9:
			GPIO.setup(leds[x],GPIO.OUT)
			GPIO.output(leds[x],GPIO.HIGH)
			x +=1
		time.sleep(0.03)
		resetLEDS()
		time.sleep(0.3)
		x=0
		y +=1
		
############################################################################################################		
# Light specific place on a particular light bank		
############################################################################################################	
def lightLEDS( lightbank, place) :
	x = 0
	y = 0
	x = lightbank * 3 - 4
	while y < place -1:
		GPIO.setup(leds[y],GPIO.OUT)
		GPIO.output(leds[y],GPIO.HIGH)
		y +=1
	while y < 3:
		GPIO.setup(leds[y],GPIO.OUT)
		GPIO.output(leds[y],GPIO.HIGH)
		y +=1
		


############################################################################################################
# GUI Widgets
############################################################################################################

############################################################################################################
# Red Circle
############################################################################################################
def redCircle():
	circleCanvas.create_oval(10, 10, 80, 80, width=0, fill='red')
	root.update()

############################################################################################################
# Yellow Circle
############################################################################################################
def yelCircle():
	circleCanvas.create_oval(20, 20, 80, 80, width=0, fill='yellow')

############################################################################################################
# Green Circle
############################################################################################################
def grnCircle():
    circleCanvas.create_oval(10, 10, 80, 80, width=0, fill='green')
    # colorLog.insert(0.0, "Green\n")

############################################################################################################
# Setup Class for full Screen
############################################################################################################	
class FullScreenApp(object):
    def __init__(self, master, **kwargs):
        self.master=master
        pad=3
        self._geom='200x200+0+0'
        master.geometry("{0}x{1}+0+0".format(
            master.winfo_screenwidth()-pad, master.winfo_screenheight()-pad))
        master.bind('<Escape>',self.toggle_geom)            
    def toggle_geom(self,event):
        geom=self.master.winfo_geometry()
        print(geom,self._geom)
        self.master.geometry(self._geom)
        self._geom=geom

############################################################################################################		
#----------------------------------------------------------------------
############################################################################################################
if __name__ == "__main__":
    path = "settings.ini"		

############################################################################################################
## Pull in INI Constants from the the file
############################################################################################################
## Configuration Information
############################################################################################################
MaxRaceTime = int(get_setting(path, 'Settings', 'max_race_time', False))
ShortRaceTime = int( get_setting(path, 'Settings', 'min_race_time', False))
BounceTime = int(get_setting(path, 'Settings', 'switch_bounce_time', False))
LaneOne = int(get_setting(path, 'Settings', 'GPIOLane1', False ))
LaneTwo = int(get_setting(path, 'Settings', 'GPIOLane2', False))
LaneThree = int(get_setting(path, 'Settings', 'GPIOLane3', False))
GPIOBounce_time = int(get_setting(path, 'Settings','GPIOBounce_time', False))
leds = get_setting2(path, 'Settings', 'Leds', False)
StartSwitch = int(get_setting(path, 'Settings', 'GPIOSwitch', False))
Unit = str(get_setting(path, 'Settings', 'Unit', False))

############################################################################################################
## Race Information
############################################################################################################
GFastestLane = int(get_setting(path, 'Races', 'GFastestLane', False))
GFastestTime = str(get_setting(path, 'Races', 'GFastestTime', False))
GFastestRaceCounter = int(get_setting(path, 'Races', 'GFastestRaceCounter', False))
RaceCounter = int(get_setting(path, 'Races','race_counter', False))

############################################################################################################
## Fix leds so that it is an array of integers
############################################################################################################
leds = list(map(int, leds))

############################################################################################################
## Setup Logging
############################################################################################################
logger = logging.getLogger('CubCar')
hdlr = logging.FileHandler('CubCar.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
## Set Logging Level to INFO
logger.setLevel(logging.INFO)
## Once everything is working log only warnings
## Logger.setLevel(logging.WARNING)
#####################################################


############################################################################################################
# Setup the GPIO's for the Lanes and the Start Switch
############################################################################################################
GPIO.setwarnings(False)
GPIO.setmode (GPIO.BOARD)
GPIO.setup(LaneOne,GPIO.IN,pull_up_down = GPIO.PUD_UP)
GPIO.setup(LaneTwo,GPIO.IN,pull_up_down = GPIO.PUD_UP)
GPIO.setup(LaneThree,GPIO.IN,pull_up_down = GPIO.PUD_UP)
GPIO.setup(StartSwitch,GPIO.IN, pull_up_down = GPIO.PUD_UP)

############################################################################################################		
# Setup Listener Events on the GPIO
############################################################################################################
if GPIOBounce_time == 0:
	GPIO.add_event_detect(LaneOne, GPIO.RISING)
	GPIO.add_event_detect(LaneTwo, GPIO.RISING)
	GPIO.add_event_detect(LaneThree, GPIO.RISING)

else:
	GPIO.add_event_detect(LaneOne, GPIO.RISING, bouncetime = GPIOBounce_time)
	GPIO.add_event_detect(LaneTwo, GPIO.RISING, bouncetime = GPIOBounce_time)
	GPIO.add_event_detect(LaneThree, GPIO.RISING, bouncetime = GPIOBounce_time)

############################################################################################################
# create matrix device
############################################################################################################
serial = spi(port=0, device=0, gpio=noop())
device = max7219(serial, cascaded=4, block_orientation=-90)

print("Created device")
	
############################################################################################################	
# Open GUI
############################################################################################################
root = Tk() #Makes the window
app=FullScreenApp(root)
root.wm_title("Race Day") #Makes the title that will appear in the top left
root.config(background = "#FFFFFF")

############################################################################################################
# configure a default font
############################################################################################################
myfont = tkFont.Font(family='Helvetica',size=20, weight = "bold")
myfont2 = tkFont.Font(family='Helvetica',size=12, weight = "bold")
		
############################################################################################################		
#Left Frame and its contents
############################################################################################################
leftFrame = Frame(root, width=1, height = 1)
leftFrame.grid(row=0, column=0, padx=2, pady=2)

############################################################################################################
# Right Frame and its contents
############################################################################################################
rightFrame = Frame(root, width=1, height = 1, relief = RIDGE )
rightFrame.grid(row=0, column=1, padx=10, pady=10)

############################################################################################################
# Start filling the left frame
############################################################################################################
Label(leftFrame, text="Ready to Race", width = 20, font = myfont, relief = RIDGE ).grid(columnspan=2,row=0, column=0, padx=4, pady=2)

############################################################################################################
# Create Ready to Race circleCanvas
############################################################################################################
circleCanvas = Canvas(leftFrame, width=100, height=100, bg='white')
circleCanvas.grid(columnspan=2, row=1, column=0, padx=10, pady=2, sticky = N )

############################################################################################################
# Add Race counter
############################################################################################################
Label(leftFrame, text="Race Counter", width = 20, font = myfont, relief = RIDGE ).grid(columnspan=2, row=2, column=0, padx=2, pady=2)
RCounter = Text(leftFrame, width = 5, height = 1, takefocus=0, font=myfont2)
RCounter.grid(columnspan=2,row=3, column=0, padx=2, pady=8)

############################################################################################################
# Fastest Racer Today
############################################################################################################
Label(leftFrame, text="Fastest Time Today",width = 20, font = myfont, relief = RIDGE ).grid(columnspan=2,row=4, column=0, padx=10, pady=1)

Label(leftFrame, text="Lane", font = myfont2).grid(row=5, column=0, padx=1, pady=1)
FastestLane = Text(leftFrame, width = 12, height = 1, takefocus=0, font=myfont2)
FastestLane.grid(row=5, column=1, padx=2, pady=2)

Label(leftFrame, text="Time", font = myfont2).grid(row=6, column=0, padx=1, pady=1)
FastestTime = Text(leftFrame, width = 12, height = 1, takefocus=0, font=myfont2)
FastestTime.grid(row=6, column=1, padx=2, pady=2)

Label(leftFrame, text="Race", font = myfont2).grid(row=7, column=0, padx=1, pady=1)
FastestRace = Text(leftFrame, width = 12, height = 1, takefocus=0, font=myfont2)
FastestRace.grid(row=7, column=1, padx=2, pady=2)

############################################################################################################
## Load Graphic of the car (Does not work with smaller screen)
############################################################################################################
# try:
#    imageEx = PhotoImage(file = 'image.gif')
#    Label(leftFrame, image=imageEx).grid(row=8, column=0, padx=2, pady=2)
# except:
#    print("Image not found")
############################################################################################################

############################################################################################################
# Labels on Right Frame
############################################################################################################
Label(rightFrame, text="Current Race", width = 20, font = myfont, relief = RIDGE).grid(columnspan=2, row=0, column=0, padx=2, pady=2)

RaceLog = Text(rightFrame, width = 30, height = 10, takefocus=0)
RaceLog.grid(columnspan=2,row=14, column=0, padx=2, pady=2)

############################################################################################################
# Create labels and inputs for the various Lanes
############################################################################################################
Label(rightFrame, text=" 1st", font = myfont).grid(row=5, column=0, sticky = W,  padx=2, pady=2)
Label(rightFrame, text="", font = myfont2).grid(row=4, column=1, sticky = S,  padx=2, pady=1)

Label(rightFrame, text=" 2nd", font = myfont).grid(row=7, column=0, sticky = W, padx=2, pady=2)
Label(rightFrame, text="", font = myfont2).grid(row=6, column=1, sticky = S,  padx=2, pady=1)

Label(rightFrame, text=" 3rd", font = myfont).grid(row=9, column=0, sticky = W, padx=2, pady=2)
Label(rightFrame, text="", font = myfont2).grid(row=8, column=1, sticky = S,  padx=2, pady=1)

LLane1 = Text(rightFrame, width = 18, height = 1, takefocus=0, font=myfont)
LLane1.grid(row=5, column=1, sticky = S,  padx=10, pady=1)

LLane2 = Text(rightFrame, width = 18, height = 1, takefocus=0, font=myfont)
LLane2.grid(row=7, column=1, sticky = S,  padx=10, pady=1)

LLane3 = Text(rightFrame, width = 18, height = 1, takefocus=0, font=myfont)
LLane3.grid(row=9, column=1, sticky = S,  padx=10, pady=1)

############################################################################################################
## Button Frame
############################################################################################################
btnFrame = Frame(rightFrame, width=30, height = 3,relief = RIDGE )
btnFrame.grid(row=10, column=0, padx=10, pady=5, columnspan = 2)

RedBtn = Button(btnFrame, text="Red", command=redCircle)
RedBtn.grid(row=0, column=2, padx=10, pady=2)


############################################################################################################
# Start the Main Loop
############################################################################################################
def my_mainloop():
		
	## Reference the Global RaceCounter
	global RaceCounter 
	## Reference the Global LEDs
	global leds
	## Global Fastest Times Today
	global GFastestLane
	global GFastestTime
	global GFastestRaceCounter
	## For future if multiple units are linked :-)
	global Unit
			
	while 1:

		RaceCounter +=1  # Increment Race Counter
		RCounter.delete(1.0, END)
		Msg = " " + str(RaceCounter) 
		RCounter.insert(0.0, Msg)	
		
		print ("Press start Button")
		RaceLog.insert(0.0, "Press Start\n")
		redCircle()
		root.update()
		msg = "Let's Race!!!!"
		show_message(device, msg, fill="white", font=proportional(CP437_FONT), scroll_delay=0.05)
		
		# wait for start button to be pushed
		GPIO.wait_for_edge(StartSwitch, GPIO.RISING, bouncetime = BounceTime )
		
		# time.sleep(3)
		
        # Turn all LED's off
		resetLEDS()
		LLane1.delete(1.0, END)
		LLane2.delete(1.0, END)
		LLane3.delete(1.0, END)
		root.update()
		
		# wait for start button to be released
		print ("Release start Button")
		RaceLog.insert(0.0, "Release Start\n")
		grnCircle()
		root.update()
		GPIO.wait_for_edge(StartSwitch, GPIO.RISING, bouncetime = BounceTime )	
		
		# time.sleep(3)
		
		# Start the Race!!
		flashLEDS()
		print( "Racers Away")
		with canvas(device) as draw:
			text(draw, (0, 0), "G0!!", fill="white")
		time.sleep(0.1)
		for _ in range(2):
			for intensity in range(16):
				device.contrast(intensity * 16)
				time.sleep(0.01)
		device.contrast(0x80)
		
		RaceLog.insert(0.0, "Racers Away\n")
		root.update()
					
		# Capture Race start time
		StartTime = time.time()

		FirstPlace = 0  						# What lane ended up in first Place
		SecondPlace = 0 						# What lane ended up in Second Place
		ThirdPlace = 0  						# What lane ended up in Third Place
		LaneOneFinishTime = 0 					# Time when Lane 1 Finished Race
		LaneTwoFinishTime  = 0 					# Time when Lane 2 Finished Race
		LaneThreeFinishTime = 0 				# Time When Lane 3 Finished Race
		Finishers = 0  							# Count of how many cars have completed the Race
		ident = " + "
		GFastestRaceIndicator = 0				# Indicator that a new fastest time has happened
		Msg1 = "  Lane 1  -  DNF"				# Set lanes to DNF as a default
		Msg2 = "  Lane 2  -  DNF"				# Set lanes to DNF as a default
		Msg3 = "  Lane 3  -  DNF"				# Set lanes to DNF as a default
                	
		# Race Started - Run Until Timeout or all 3 racers finished
		while (time.time() - StartTime) < MaxRaceTime and Finishers < 3:	
		
			if GPIO.event_detected( LaneOne ):	
				# print( "H1" )
				if ( time.time() - StartTime ) > ShortRaceTime:
					# print ("H2")
					if LaneOneFinishTime == 0:			# Check and see if a time has been recorded for Lane 1 to finish.  (Way to deal with multiple events)
						LaneOneFinishTime = time.time()
						Finishers +=1                   #  Add 1 to count of racers who have finished
						# Calculate time difference
						diff_time = (LaneOneFinishTime - StartTime)
						Msg1 = "  Lane 1  -  " + str(diff_time)[0:7] 
						print(Msg1)
						
						if (GFastestTime == 0)	or 	(diff_time < GFastestTime) : 		# if no fastest time has been recorded or new fastest time
							GFastestTime = diff_time
							GFastestLane = "1"
							GFastestRaceCounter = RaceCounter
							FastestLane.delete(1.0, END)
							FastestLane.insert(0.0, GFastestLane)
							FastestTime.delete(1.0, END)
							FastestTime.insert(0.0, str(diff_time))
							FastestRace.delete(1.0,END)
							FastestRace.insert(0.0, str(RaceCounter))
							GFastestRaceIndicator = 1				
																		
						if FirstPlace == 0:				# If First place not already taken, then fill it.
							FirstPlace = 1
							LLane1.delete(1.0, END)			# post to GUI
						 	LLane1.insert(0.0, Msg1)
							GPIO.setup(leds[2],GPIO.OUT)
							GPIO.output(leds[2],GPIO.HIGH)
							GPIO.setup(leds[1],GPIO.OUT)
							GPIO.output(leds[1],GPIO.LOW)
							GPIO.setup(leds[0],GPIO.OUT)
							GPIO.output(leds[0],GPIO.LOW)
						elif SecondPlace == 0:			# Else If Second Place not taken, then fill it.
							SecondPlace = 1
							LLane2.delete(1.0, END)			# post to GUI
						 	LLane2.insert(0.0, Msg1)
							GPIO.setup(leds[2],GPIO.OUT)
							GPIO.output(leds[2],GPIO.HIGH)
							GPIO.setup(leds[1],GPIO.OUT)
							GPIO.output(leds[1],GPIO.HIGH)
							GPIO.setup(leds[0],GPIO.OUT)
							GPIO.output(leds[0],GPIO.LOW)
						elif ThirdPlace == 0:			# Else if Third Place not taken, then fill it.
							ThirdPlace = 1
							LLane3.delete(1.0, END)			# post to GUI
						 	LLane3.insert(0.0, Msg1)
							GPIO.setup(leds[2],GPIO.OUT)
							GPIO.output(leds[2],GPIO.HIGH)
							GPIO.setup(leds[1],GPIO.OUT)
							GPIO.output(leds[1],GPIO.HIGH)
							GPIO.setup(leds[0],GPIO.OUT)
							GPIO.output(leds[0],GPIO.HIGH)							
					
			if GPIO.event_detected( LaneTwo ):	
				if ( time.time() - StartTime ) > ShortRaceTime:
					if LaneTwoFinishTime == 0:
						LaneTwoFinishTime = time.time()
						Finishers +=1
						diff_time = (LaneTwoFinishTime - StartTime)
						Msg2 = "  Lane 2  -  " + str(diff_time)[0:7] 
						print(Msg2)
						if (GFastestTime == 0)	or 	(diff_time < GFastestTime) :		# if no fastest time has been recorded or new fastest time
							GFastestTime = diff_time
							GFastestLane = "2"
							GFastestRaceCounter = RaceCounter
							FastestLane.delete(1.0, END)
							FastestLane.insert(0.0, GFastestLane)
							FastestTime.delete(1.0, END)
							FastestTime.insert(0.0, str(diff_time))
							FastestRace.delete(1.0,END)
							FastestRace.insert(0.0, str(RaceCounter))
							GFastestRaceIndicator = 1
						
						if FirstPlace == 0:
							FirstPlace = 2
							LLane1.delete(1.0, END)			# post to GUI
						 	LLane1.insert(0.0, Msg2)
							GPIO.setup(leds[5],GPIO.OUT)
							GPIO.output(leds[5],GPIO.HIGH)
							GPIO.setup(leds[4],GPIO.OUT)
							GPIO.output(leds[4],GPIO.LOW)
							GPIO.setup(leds[3],GPIO.OUT)
							GPIO.output(leds[3],GPIO.LOW)
							
						elif SecondPlace == 0:
							SecondPlace = 2
							LLane2.delete(1.0, END)			# post to GUI
						 	LLane2.insert(0.0, Msg2)
							GPIO.setup(leds[5],GPIO.OUT)
							GPIO.output(leds[5],GPIO.HIGH)
							GPIO.setup(leds[4],GPIO.OUT)
							GPIO.output(leds[4],GPIO.HIGH)
							GPIO.setup(leds[3],GPIO.OUT)
							GPIO.output(leds[3],GPIO.LOW)
						elif ThirdPlace == 0:
							ThirdPlace = 2
							LLane3.delete(1.0, END)			# post to GUI
						 	LLane3.insert(0.0, Msg2)
							GPIO.setup(leds[5],GPIO.OUT)
							GPIO.output(leds[5],GPIO.HIGH)
							GPIO.setup(leds[4],GPIO.OUT)
							GPIO.output(leds[4],GPIO.HIGH)
							GPIO.setup(leds[3],GPIO.OUT)
							GPIO.output(leds[3],GPIO.HIGH)
					
			if GPIO.event_detected( LaneThree ):	
				if ( time.time() - StartTime ) > ShortRaceTime:
					if LaneThreeFinishTime == 0:
						LaneThreeFinishTime = time.time()
						Finishers +=1
						diff_time = (LaneThreeFinishTime - StartTime)
						
						Msg3 = "  Lane 3  -  " + str(diff_time)[0:7]
						print(Msg3)
						
						if (GFastestTime == 0)	or 	(diff_time < GFastestTime) : 		# if no fastest time has been recorded or new fastest time
							GFastestTime = diff_time
							GFastestLane = "3"
							GFastestRaceCounter = RaceCounter
							FastestLane.delete(1.0, END)
							FastestLane.insert(0.0, GFastestLane)
							FastestTime.delete(1.0, END)
							FastestTime.insert(0.0, str(diff_time))
							FastestRace.delete(1.0,END)
							FastestRace.insert(0.0, str(RaceCounter))
							GFastestRaceIndicator = 1
						
						if FirstPlace == 0:
							FirstPlace = 3
							LLane1.delete(1.0, END)			# post to GUI
						 	LLane1.insert(0.0, Msg3)
							GPIO.setup(leds[8],GPIO.OUT)
							GPIO.output(leds[8],GPIO.HIGH)
							GPIO.setup(leds[7],GPIO.OUT)
							GPIO.output(leds[7],GPIO.LOW)
							GPIO.setup(leds[6],GPIO.OUT)
							GPIO.output(leds[6],GPIO.LOW)
						elif SecondPlace == 0:
							SecondPlace = 3
							LLane2.delete(1.0, END)			# post to GUI
						 	LLane2.insert(0.0, Msg3)
							GPIO.setup(leds[8],GPIO.OUT)
							GPIO.output(leds[8],GPIO.HIGH)
							GPIO.setup(leds[7],GPIO.OUT)
							GPIO.output(leds[7],GPIO.HIGH)
							GPIO.setup(leds[6],GPIO.OUT)
							GPIO.output(leds[6],GPIO.LOW)
						elif ThirdPlace == 0:
							ThirdPlace = 3
							LLane3.delete(1.0, END)			# post to GUI
						 	LLane3.insert(0.0, Msg3)
							GPIO.setup(leds[8],GPIO.OUT)
							GPIO.output(leds[8],GPIO.HIGH)
							GPIO.setup(leds[7],GPIO.OUT)
							GPIO.output(leds[7],GPIO.HIGH)
							GPIO.setup(leds[6],GPIO.OUT)
							GPIO.output(leds[6],GPIO.HIGH)
					
		root.update()
		
		# If all 3 racers have finished print stats
		Msg = str(FirstPlace) + " " + str(SecondPlace) + " " + str(ThirdPlace)
		# print(Msg)
						
		# print(str(RaceCounter)+ " Races Run")
		# time.sleep(int(5))
        
		############################################################################################################
		## Post an update to the Settings File and the Logging
		############################################################################################################
		Msg = Unit + "|" + str(RaceCounter) + "|" + Msg1 + "|" +  Msg2 + "|"+ Msg3
		logger.info(Msg)
				
		if GFastestRaceIndicator == 1 :						##  If a fastest Race Happened - Log it
			dispMsg = "Log Fastest Race"
			 # print(dispMsg)
			logger.info(dispMsg)
			update_setting(path, "Races", "GFastestLane", GFastestLane)
			update_setting(path, "Races", "GFastestRaceCounter", RaceCounter)
			update_setting(path, "Races", "GFastestTime", GFastestTime)
        
root.after(200, my_mainloop)

############################################################################################################
## Start the GUI and Run the Main Loop
############################################################################################################

try:
	testLEDS()
	flashLEDS()
	# Start the GUI
	root.mainloop()

except KeyboardInterrupt:  
    # here you put any code you want to run before the program   
    # exits when you press CTRL+C  
    print "\n", RaceCounter # print value of counter  
	
except:
	print("Issue has been found")
	
finally:
	update_setting(path, "Races", "race_counter", RaceCounter)
	GPIO.cleanup()
	root.quit()
	print("Clean up and close")

