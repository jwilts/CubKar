#file -- RaceManager.py --
#!/usr/bin/env python

############################################################################################################
##	Version: 2.1
##  Date: Jan 5/2020
##  - Combine separate apps that manage RFID and run timer into a single application
##  
############################################################################################################
## Notes:
## You cannot load both the Matrix and the RF ID pad at the same time. So you will need to disable one 
## or the other. See lines directly below the comment block.
## Code should work both with python2 and python3
## Program is designed to work with MariaDB Database or just using a file logger.
## 
## Relay is a future consideration to allow for secondary button on RF PAD to kick off relay.
###########################################################################################################

global LoadRFPAD 
LoadRFPAD = "true"
global LoadMatrix 
LoadMatrix = "true"

import os
import logging
import re
import argparse

import sys

import time 
import sys
import RPi.GPIO as GPIO

import mysql.connector

if sys.version_info[0] == 3:
    # for Python3
    from tkinter import *   ## notice lowercase 't' in tkinter here
    import tkinter.font as tkFont
    import configparser
else:
    # for Python2
    from Tkinter import *   ## notice capitalized T in Tkinter
    import tkFont
    import ConfigParser
   


## from  LightsRelays import *   ## Library I wrote
## from  SettingsInfo import *   ## Library I wrote

############################################################################################################
## load RC522 info
## cant load matrix and RFID pad at the same time.
############################################################################################################
if LoadRFPAD == "true":
    from mfrc522 import SimpleMFRC522

## Turn on the debugger if the program is being stupid.
import pdb; pdb.set_trace()

# from threading import Thread

############################################################################################################
	
##  ------  Function Definitions

if sys.version_info[0] == 3:
    # for Python3
    from tkinter import *   ## notice lowercase 't' in tkinter here
    import tkinter.font as tkFont
    import configparser
else:
    # for Python2
    from Tkinter import *   ## notice capitalized T in Tkinter
    import tkFont
    import ConfigParser

############################################################################################################		
#----------------------------------------------------------------------
############################################################################################################
    		

############################################################################################################
## Create a config file
############################################################################################################
def create_config(path):
    if sys.version_info[0] == 3:
        # for Python3
        config = configparser.configparser()
        
    else:
        # for Python2
        config = ConfigParser.ConfigParser()
        
    config.add_section("Settings")
    config.set("Settings", "max_race_time", "")
    config.set("Settings", "min_race_time", "")
    config.set("Settings", "GPIO_relay_1", "")
    config.set("Settings", "GPIO_track_switch","")   
    config.set("Settings", "track_switch_bounce_time", "")
    config.set("Settings", "GPIO_car_select_switch", "")
    config.set("Settings", "car_select_bounce_time", "")
    config.set("Settings", "GPIO_pad_switch", "")
    config.set("Settings", "pad_switch_bounce_time", "") 
    config.set("settings", "Leds","")
    config.set("Settings", "GPIO_ldr_lane_1", "")
    config.set("Settings", "GPIO_ldr_lane_2", "")
    config.set("Settings", "GPIO_ldr_lane_3", "")  
    config.set("settings", "Unit","")
    config.set("settings", "Matrix_YN","")
    
    config.set("dbase", "use_database_YN", "")
    config.set("dbase", "Host", "")
    config.set("dbase", "User", "")
    config.set("dbase", "Passwd", "")
    config.set("dbase", "Database", "")
    
    config.set("Races", "GFastestLane", "")
    config.set("Races", "GFastestTime", "")
    config.set("Races", "GFastestRaceCounter", "")	
    config.set("Races", "race_counter","")
    config.set("Races", "Heat","")
    with open(path, "wb") as config_file:
        config.write(config_file)

		
############################################################################################################		
## Return a Config object		
############################################################################################################
def get_config(path):
    if not os.path.exists(path):
        create_config(path)
	
    if sys.version_info[0] == 3:
        # for Python3
        config = configparser.ConfigParser()
        
    else:
        # for Python2
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
        print(" %r, %r, %r" % (section, setting, value))
    return value

############################################################################################################	
## Read an Array delimited by commas	
############################################################################################################
def get_setting2(path, section, setting, diplay):
    config = get_config(path)
    value = config.get(section, setting).split(',')
	
    if diplay == True:
        print(" %r, %r, %r" % (section, setting, value))
    return value
	
############################################################################################################	
## Update a Setting	
############################################################################################################
def update_setting(path, section, setting, value):
    config = get_config(path)
    config.set(section, setting, str(value))
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
## Pull in INI Constants from the the file
############################################################################################################
## Configuration Information
############################################################################################################
path = "RMsettings.ini"
MaxRaceTime = int(get_setting(path, 'Settings', 'max_race_time', True))
ShortRaceTime = int( get_setting(path, 'Settings', 'min_race_time', True))
Unit = str(get_setting(path, 'Settings', 'Unit', True))
MatrixYN = str(get_setting(path, 'Settings', 'matrix_yn', True))

############################################################################################################
## GPIO Information
############################################################################################################
TrackBounceTime = int(get_setting(path, 'Settings', 'track_switch_bounce_time', True))
LDRLaneOne = int(get_setting(path, 'Settings', 'GPIO_ldr_lane_1', True ))
LDRLaneTwo = int(get_setting(path, 'Settings', 'GPIO_ldr_lane_2', True))
LDRLaneThree = int(get_setting(path, 'Settings', 'GPIO_ldr_lane_3', True))
track_switch_bounce_time = int(get_setting(path, 'Settings','track_switch_bounce_time', True))
leds = get_setting2(path, 'Settings', 'Leds', True)
leds = list(map(int, leds))         ## Fix leds so that it is an array of integers
ledsB1 = leds[0:2]
ledsB2 = leds[3:5]
ledsB3 = leds[6:8]

TrackSwitch = int(get_setting(path, 'Settings', 'GPIO_track_switch', True))

GPIO_relay_1 = int(get_setting(path, 'Settings', 'GPIO_relay_1', True))
car_select_bounce_time = int( get_setting(path, 'Settings', 'car_select_bounce_time', True))
pad_switch_bounce_time = int( get_setting(path, 'Settings', 'pad_switch_bounce_time', True))
GPIO_car_select_switch = int( get_setting(path, 'Settings', 'GPIO_car_select_switch', True))
GPIO_pad_switch = int( get_setting(path, 'Settings', 'GPIO_pad_switch', True))

############################################################################################################
## Database Information
############################################################################################################
DBaseYN = str(get_setting(path, 'dbase', 'use_database_YN', True))
Host = str(get_setting(path, 'dbase', 'host', True))
User = str(get_setting(path, 'dbase', 'user', True))
passwd = str(get_setting(path, 'dbase', 'passwd', True))
database = str(get_setting(path, 'dbase', 'database', True))

############################################################################################################
## Race Information
############################################################################################################
GFastestLane = int(get_setting(path, 'Races', 'GFastestLane', True))
GFastestTime = float(get_setting(path, 'Races', 'GFastestTime', True))
GFastestRaceCounter = int(get_setting(path, 'Races', 'GFastestRaceCounter', True))
RaceCounter = int(get_setting(path, 'Races','race_counter', True))
Heat = int(get_setting(path, 'Races', 'Heat', True))


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
## load 8x8 matrix info
## cant load matrix and RFID pad at the same time.
############################################################################################################
if LoadMatrix == "true":
    from luma.led_matrix.device import max7219
    from luma.core.interface.serial import spi, noop
    from luma.core.render import canvas
    from luma.core.virtual import viewport
    from luma.core.legacy import text, show_message
    from luma.core.legacy.font import proportional, CP437_FONT, TINY_FONT, SINCLAIR_FONT, LCD_FONT

############################################################################################################
# create matrix device
############################################################################################################
if LoadMatrix == "true":
    serial = spi(port=0, device=0, gpio=noop())
    device = max7219(serial, cascaded=4, block_orientation=-90)
    print("Created device")
else :
    print("No Matrix loaded")


############################################################################################################
# Reset LED's to an off state
############################################################################################################
def resetLEDS():
	x = 0
	while x < len(leds):
		GPIO.setup(leds[x],GPIO.OUT)
		GPIO.output(leds[x],GPIO.LOW)
		x +=1
		
############################################################################################################		
# Run test cycle of the LEDs
############################################################################################################
def testLEDS():
    x = 0
    while x < len(leds) :
        GPIO.setup(leds[x],GPIO.OUT)
        GPIO.output(leds[x],GPIO.LOW)
        x +=1
    
        # Run test cycle of the LEDs
        x = 0
        while x < len(leds):
            GPIO.setup(leds[x],GPIO.OUT)

            GPIO.output(leds[x],GPIO.HIGH)
            time.sleep(0.2)
            # GPIO.output(leds[x],GPIO.LOW)
            x +=1
        time.sleep(2)
        x = 0

        # Turn LED's Off
        while x < len(leds):
            GPIO.setup(leds[x],GPIO.OUT)
            GPIO.output(leds[x],GPIO.LOW)
            x +=1

############################################################################################################		
# 3 quick flashes of the LEDS		
############################################################################################################
def flashLEDS() :
	
	x = 0
	y = 0
	while y < 3:
		while x < len(leds):
			GPIO.setup(leds[x],GPIO.OUT)
			GPIO.output(leds[x],GPIO.HIGH)
			x +=1
		time.sleep(0.03)
		resetLEDS()
		time.sleep(0.1)
		x=0
		y +=1

############################################################################################################		
# Light all LED's in the bank	
############################################################################################################
def lightLEDS() :
	
	x = 0
	y = 0
	while y < len(leds):
		while x < len(leds):
			GPIO.setup(leds[x],GPIO.OUT)
			GPIO.output(leds[x],GPIO.HIGH)
			x +=1
		x=0
		y +=1


############################################################################################################		
# Light all LED's in specified bank	
############################################################################################################
def LightLEDBank(LightBank) :
	
    if LightBank == 1:
        x = 0
        while x < 3:
            GPIO.setup(leds[x],GPIO.OUT)
            GPIO.output(leds[x],GPIO.HIGH)
            x +=1
        
    elif LightBank == 2:
        x = 3
        while x < 6:
            GPIO.setup(leds[x],GPIO.OUT)
            GPIO.output(leds[x],GPIO.HIGH)
            x +=1
        
    elif LightBank == 3:
        x = 6
        while x < 9:
            GPIO.setup(leds[x],GPIO.OUT)
            GPIO.output(leds[x],GPIO.HIGH)
            x +=1
    else:
        print("Whoops")   	

############################################################################################################		
# Turn off Relay	
############################################################################################################
def TurnRelayOff() :
       
    GPIO.output(GPIO_relay_1,GPIO.LOW)


############################################################################################################		
# Turn off Relay	
############################################################################################################
def TurnRelayOn() :
    
    GPIO.output(GPIO_relay_1,GPIO.HIGH)
    sleep(1)
    GPIO.output(GPIO_relay_1,GPIO.LOW)
    



############################################################################################################
# Setup the GPIO's states 
############################################################################################################
GPIO.setwarnings(False)
GPIO.setmode (GPIO.BOARD)                                       ## Use GPIO PIN #'s instead of GPIO ID's.
GPIO.setup(LDRLaneOne,GPIO.IN,pull_up_down = GPIO.PUD_UP)
GPIO.setup(LDRLaneTwo,GPIO.IN,pull_up_down = GPIO.PUD_UP)
GPIO.setup(LDRLaneThree,GPIO.IN,pull_up_down = GPIO.PUD_UP)
GPIO.setup(TrackSwitch,GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(GPIO_car_select_switch,GPIO.IN,pull_up_down = GPIO.PUD_UP)
GPIO.setup(GPIO_pad_switch,GPIO.IN,pull_up_down = GPIO.PUD_UP)
GPIO.setup(GPIO_relay_1,GPIO.OUT)                               ## Set Relay to be an OUT

############################################################################################################		
# Setup Listener Events on the GPIO
############################################################################################################
GPIO.add_event_detect(LDRLaneOne, GPIO.RISING, bouncetime = track_switch_bounce_time)
GPIO.add_event_detect(LDRLaneTwo, GPIO.RISING, bouncetime = track_switch_bounce_time)
GPIO.add_event_detect(LDRLaneThree, GPIO.RISING, bouncetime = track_switch_bounce_time)
GPIO.setup(GPIO_car_select_switch, GPIO.IN)                 ## As we want program to stop on car select process we dont want a regular event detect.
                                                            ## dont know why but this seems to work.
# GPIO.add_event_detect(GPIO_car_select_switch, GPIO.RISING)
GPIO.add_event_detect(GPIO_pad_switch, GPIO.RISING)


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

LLane1 = Text(rightFrame, width = 18, height = 2, takefocus=0, font=myfont)
LLane1.grid(row=5, column=1, sticky = S,  padx=10, pady=1)

LLane2 = Text(rightFrame, width = 18, height = 2, takefocus=0, font=myfont)
LLane2.grid(row=7, column=1, sticky = S,  padx=10, pady=1)

LLane3 = Text(rightFrame, width = 18, height = 2, takefocus=0, font=myfont)
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
    ## In case there are multiple units
    global Unit
    ## What heat are we in. Reset between heats.  (Future consider having this set in the database, or prompting at startup)
    global Heat
    global MatrixYN
    
    global id      
    global CurrentTrack
    
    global dbStruct
    
    dbStruct = []    # Create empty structure for putting database records into.
    
      
    ## db = mysql.connector.connect(
    ## host='"' + Host + '"',
    ## user='"' + User + '"',
    ## passwd='"' + passwd + '"',
    ## database='"' + database + '"'
    ## )   
    
    db = mysql.connector.connect(
    # host="localhost",
    host="localhost",
    user="root",
    passwd="bingo",
    database="CubCar"
    )

    cursor = db.cursor()  ## for Database interactions
    
    while 1:
            
        RaceCounter +=1  # Increment Race Counter
        RCounter.delete(1.0, END)
        Msg = " " + str(RaceCounter) 
        RCounter.insert(0.0, Msg)	
		
        print ("Press start Button")
        RaceLog.insert(0.0, "Press Start\n")
        redCircle()
        root.update()
        
        if MatrixYN == 'Y':
            msg = "Let's Race!!!!"
            show_message(device, msg, fill="white", font=proportional(CP437_FONT), scroll_delay=0.05)
		
        ## wait for start button to be pushed
        ## At this point the switch on the track should get closed and cars get loaded.
        GPIO.wait_for_edge(TrackSwitch, GPIO.RISING, bouncetime = TrackBounceTime )
        
        # time.sleep(3)
		
        # Turn all LED's off
        resetLEDS()
        # clear the GUI for the 3 lanes
        LLane1.delete(1.0, END)
        LLane2.delete(1.0, END)
        LLane3.delete(1.0, END)
        root.update()
        
        dbStruct.clear() # Empty the database structure
        
        ## All the code for the RFID PAD goes here.
        if LoadRFPAD == True :
        
            reader = SimpleMFRC522()
            
            while 1:
        
                OldText = ''
                OldID = ''
                CurrentTrack = 0
            
                RaceCounter +=1  # Increment Race Counter
          
                resetLEDS()   
                
                while CurrentTrack < 3:
                    id = ''
                    MSG = ''
                    print("Waiting for Car")
                    id, text = reader.read()
                    
                    # Make sure cars have changed on pad
                    if id != OldID:
                        MSG = "ID:" + str(id) + "\n OldID:" + str(OldID) + "\n Text:" + str(text) + "\n CurrentTrack:" + str(CurrentTrack)
                        print(MSG)
                        
                        OldID = id
                    
                        if str(text) == "skip" :
                            print("Don't count this car!!")
                                
                        resetLEDS()
                        print("Load track %d then press button 1" % (CurrentTrack+1))
                        
                        ## Highlight correct light bank
                        LightLEDBank(CurrentTrack+1)
                        
                        ## UPDATE RacerName List
                        
                        ## Lookup RacerName and Car Name from Database
                        sql = "SELECT ID, RacerFirstName, RacerLastName, RacerPack,RacerCarName, RacerRFID, RacerCarClass from RacerInfo WHERE ID= "+ str(id)
                        cursor.execute(sql)
                        result = cursor.fetchone()
                        
                        if cursor.rowcount >= 1:
                            print("Welcome " + result[1])
                            RaceLog.insert(0.0, "Welcome " + result[1] )
                            if CurrentTrack == 0:
                                Lane1CarID = result[0]
                                Lane1ID = str(id)
                                Lane1Name = result[1] + " " + result[2]
                                Lane1FirstName = result{1]
                                Lane1LastName = result[2]
                                Lane1Pack = result[3]
                                Lane1CareName = result[4]
                                Lane1RFID = result[5]
                                
                            if CurrentTrack == 1:
                                Lane2CarID = result[0]
                                Lane2ID = str(id)
                                Lane2Name = result[1] + " " + result{2]
                                Lane2FirsName = result[1]
                                Lane2LastName = result[2]
                                Lane2Pack = result[3]
                                Lane2CarName = result[4]
                                Lane2RFID = result[5]
                            if CurrentTrack == 2:
                                Lane3CarID = result[0]
                                Lane3ID = str(id)
                                Lane3Name = result[1] + " " + result[2]
                                Lane3FirstName = result[1]
                                Lane3LastName = result[2]
                                Lane3Pack = result[3]
                                Lane3CarName = result[4]
                                Lane3RFID = result[5]
                        else:
                            print("Car Not Found")
                            RaceLog.insert(0.0, "Car Not Found" )

                        GPIO.wait_for_edge(GPIO_car_select_switch, GPIO.RISING, bouncetime = car_select_bounce_time )
                        # Turn all LED's off
                        resetLEDS()
                
                        # wait for start button to be released
                        print ("Release start Button")
                
                        GPIO.wait_for_edge(GPIO_car_select_switch, GPIO.RISING, bouncetime = car_select_bounce_time )
                         
                        CurrentTrack +=1
                        time.sleep(0.8)
                    ## End if car hasn't changed on the PAD    
              
            # End Loop  All 3 cars are loaded time to kick off the race
            
        ## End of IF for RFPAD
            
                
        ## After all the cars have been loaded and recorded then wait for the start button.
        # wait for start button to be released
        print ("Release start Button")
        RaceLog.insert(0.0, "Release Start\n")
        grnCircle()
        root.update()
        GPIO.wait_for_edge(TrackSwitch, GPIO.RISING, bouncetime = TrackBounceTime )	
		
        # time.sleep(3)
        
        # Start the Race!!
        flashLEDS()
        print( "Racers Away")
        
        if MatrixYN == 'Y' :
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

        Lane1Place = 0                          # Needed for Database 
        Lane2Place = 0                          # Needed for database
        Lane3Place = 0                          # Needed for Database
        
        FirstPlace = 0  						# What lane ended up in first Place
        SecondPlace = 0 						# What lane ended up in Second Place
        ThirdPlace = 0  						# What lane ended up in Third Place
        LDRLaneOneFinishTime = 0 					# Time when Lane 1 Finished Race
        LDRLaneTwoFinishTime  = 0 					# Time when Lane 2 Finished Race
        LDRLaneThreeFinishTime = 0 				# Time When Lane 3 Finished Race
        Finishers = 0  							# Count of how many cars have completed the Race
        ident = " + "
        GFastestRaceIndicator = 0				# Indicator that a new fastest time has happened
        Msg1 = Lane1Name + "\n  Lane 1  -  DNF"				# Set lanes to DNF as a default
        Msg2 = Lane2Name +  "\n  Lane 2  -  DNF"				# Set lanes to DNF as a default
        Msg3 = Lane3Name + "\n  Lane 3  -  DNF"				# Set lanes to DNF as a default
                	
        # Race Started - Run Until Timeout or all 3 racers finished
        while (time.time() - StartTime) < MaxRaceTime and Finishers < 3:	
		
            if GPIO.event_detected( LDRLaneOne ):	
                if ( time.time() - StartTime ) > ShortRaceTime:
                    if LDRLaneOneFinishTime == 0:			# Check and see if a time has been recorded for Lane 1 to finish.  (Way to deal with multiple events)
                        LDRLaneOneFinishTime = time.time()
                        Finishers +=1                   #  Add 1 to count of racers who have finished
                        # Calculate time difference
                        diff_time = (LDRLaneOneFinishTime - StartTime)
                        Lane1Time = str(diff_time)
                        Msg1 = Lane1Name + "\n  Lane 1  -  " + str(diff_time)[0:7] 
                        print(Msg1)
						
                        if (GFastestTime == 0)	or 	(float(diff_time) < float(GFastestTime)) : 		# if no fastest time has been recorded or new fastest time
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
                            Lane1Place = 1
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
                            Lane1Place = 2
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
                            Lane1Place = 3
					
            if GPIO.event_detected( LDRLaneTwo ):	
                if ( time.time() - StartTime ) > ShortRaceTime:
                    if LDRLaneTwoFinishTime == 0:
                        LDRLaneTwoFinishTime = time.time()
                        Finishers +=1
                        diff_time = (LDRLaneTwoFinishTime - StartTime)
                        Lane2Time = str(diff_time)
                        Msg2 = Lane2Name + "\n  Lane 2  -  " + str(diff_time)[0:7] 
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
							Lane2Place = 1
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
                            Lane2Place = 2
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
                            Lane2Place = 3
            if GPIO.event_detected( LDRLaneThree ):	
                if ( time.time() - StartTime ) > ShortRaceTime:
                    if LDRLaneThreeFinishTime == 0:
                        LDRLaneThreeFinishTime = time.time()
                        Finishers +=1
                        diff_time = (LDRLaneThreeFinishTime - StartTime)
                        Lane3Time = str(diff_time)
                        Msg3 = Lane3Name + "\n  Lane 3  -  " + str(diff_time)[0:7]
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
                            Lane3Place = 1
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
                            Lane3Place = 2
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
                            Lane3Place = 3
					
        root.update()
		
        # If all 3 racers have finished print stats
        Msg = str(FirstPlace) + " " + str(SecondPlace) + " " + str(ThirdPlace)
        # print(Msg)
		
        ## Insert into Database
        sql = "INSERT INTO racerresults( RaceCounter, Unit, Heat, Lane, CarID,CarName, RacerFirstNameName, RacerLastName, Pack, RaceTime,Placing, RFID VALUES (%d, %d, %d, %d, %s, %s, %s, %s, %s, %d, %s)"
        val = (RaceCounter, Unit, Heat, 1, Lane1CarID, Lane1CarName, Lane1FirstName, Lane1LastName, Lane1Pack, Lane1Time, Lane1RFID  )
        cursor.execute(sql, val )
        db.commit()

        val = (RaceCounter, Unit, Heat, 2, Lane2CarID, Lane2CarName, Lane2FirstName, Lane2LastName, Lane2Pack, Lane2Time, Lane2RFID  )
        cursor.execute(sql, val )
        db.commit()

        val = (RaceCounter, Unit, Heat, 3, Lane3CarID, Lane3CarName, Lane3FirstName, Lane3LastName, Lane3Pack, Lane3Time, Lane3RFID  )
        cursor.execute(sql, val )
        db.commit()

        # print(str(RaceCounter)+ " Races Run")
        # time.sleep(int(5))
        
        ############################################################################################################
        ## Post an update to the Settings File and the Logging
        ############################################################################################################
        Msg = str(Unit) + "|" + str(Heat) + "|" + str(RaceCounter) + "|" + Msg1 + "|" +  Msg2 + "|"+ Msg3
        logger.info(Msg)
				
        if GFastestRaceIndicator == 1 :						##  If a fastest Race Happened - Log it
            dispMsg = "Log Fastest Race"
            # print(dispMsg)
            logger.info(dispMsg)
            # update_setting(path, "Races", "GFastestLane", str(GFastestLane))
            # update_setting(path, "Races", "GFastestRaceCounter", str(RaceCounter))
            # update_setting(path, "Races", "GFastestTime", str(GFastestTime))
        
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
    print( "\n", RaceCounter) # print value of counter  
	
except:
    print("Issue has been found")
	
finally:
    ## update_setting(path, "Races", "race_counter", str(RaceCounter))
    GPIO.cleanup()
    root.quit()
    print("Clean up and close")

