#file -- RaceManager.py --
#!/usr/bin/env python

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
##	Version: 2.3
##  Date: Feb 24 /2020
##  - Combine separate apps that manage RFID and run timer into a single application
##
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
## Notes:
## You cannot load both the Matrix and the RF ID pad at the same time. So you will need to disable one 
## or the other. See lines directly below the comment block.
## Code should work both with python2 and python3
## Program is designed to work with MariaDB Database or just using a file logger.
## if you use RF pad then you must use Database
##
## Relay is a future consideration to allow for secondary button on RF PAD to kick off relay.
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

global LoadRFPAD
LoadRFPAD = "true"
global LoadMatrix
LoadMatrix = "false"

import argparse
import logging
import mysql.connector
import os
from pprint import pprint
import re
import RPi.GPIO as GPIO
import sys
import time

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
## load RC522 info
## cant load matrix and RFID pad at the same time.
############################################################################################################
if LoadRFPAD == "true":
    from mfrc522 import SimpleMFRC522
    reader = SimpleMFRC522()

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

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
## Turn on the debugger if the program is being stupid.
## import pdb; pdb.set_trace()
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
##  Config File Routines
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

############################################################################################################
## Create a config file
## NOTE:  This is here for reference, not used by the program
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
    config.set("settings", "Leds","")
    config.set("Settings", "GPIO_ldr_lane_1", "")
    config.set("Settings", "GPIO_ldr_lane_2", "")
    config.set("Settings", "GPIO_ldr_lane_3", "")
    config.set("settings", "Unit","")
    config.set("settings", "Matrix_YN","")
    config.set("settings", "relay_yn","")

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

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
##  Load .INI settings into globals
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

############################################################################################################
## Configuration Information
############################################################################################################
path = "RMsettings.ini"
MaxRaceTime = int(get_setting(path, 'Settings', 'max_race_time', False))
ShortRaceTime = int( get_setting(path, 'Settings', 'min_race_time', False))
Unit = str(get_setting(path, 'Settings', 'Unit', False))
MatrixYN = str(get_setting(path, 'Settings', 'matrix_yn', False))
RelayYN = str(get_setting(path, 'Settings', 'relay_yn', False))

############################################################################################################
## GPIO Information
############################################################################################################
TrackBounceTime = int(get_setting(path, 'Settings', 'track_switch_bounce_time', False))
LDRLaneOne = int(get_setting(path, 'Settings', 'GPIO_ldr_lane_1', False ))
LDRLaneTwo = int(get_setting(path, 'Settings', 'GPIO_ldr_lane_2', False))
LDRLaneThree = int(get_setting(path, 'Settings', 'GPIO_ldr_lane_3', False))
track_switch_bounce_time = int(get_setting(path, 'Settings','track_switch_bounce_time', False))
leds = get_setting2(path, 'Settings', 'Leds', False)
leds = list(map(int, leds))         ## Fix leds so that it is an array of integers
ledsB1 = leds[0:2]                  ## break out LED's into banks of LED's
ledsB2 = leds[3:5]
ledsB3 = leds[6:8]

TrackSwitch = int(get_setting(path, 'Settings', 'GPIO_track_switch', False))

GPIO_relay_1 = int(get_setting(path, 'Settings', 'GPIO_relay_1', False))
car_select_bounce_time = int( get_setting(path, 'Settings', 'car_select_bounce_time', False))
GPIO_car_select_switch = int( get_setting(path, 'Settings', 'GPIO_car_select_switch', False))

############################################################################################################
## Database Information
############################################################################################################
DBaseYN = str(get_setting(path, 'dbase', 'use_database_YN', False))
Host = str(get_setting(path, 'dbase', 'host', False))
User = str(get_setting(path, 'dbase', 'user', False))
passwd = str(get_setting(path, 'dbase', 'passwd', False))
database = str(get_setting(path, 'dbase', 'database', False))

############################################################################################################
## Race Information
############################################################################################################
GFastestLane = int(get_setting(path, 'Races', 'GFastestLane', False))
GFastestTime = float(get_setting(path, 'Races', 'GFastestTime', False))
GFastestRaceCounter = int(get_setting(path, 'Races', 'GFastestRaceCounter', False))
RaceCounter = int(get_setting(path, 'Races','race_counter', False))
Heat = int(get_setting(path, 'Races', 'Heat', False))

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

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# GUI Widgets
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

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
	circleCanvas.create_oval(10, 10, 80, 80, width=0, fill='yellow')

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

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
##  Load Matrix if applicable
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

############################################################################################################
# create matrix device
############################################################################################################
if LoadMatrix == "true":
    serial = spi(port=0, device=0, gpio=noop())
    device = max7219(serial, cascaded=4, block_orientation=-90)
    print("Created device")
else :
    print("No Matrix loaded")

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
##  LED related functions
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

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
            time.sleep(0.03)
            # GPIO.output(leds[x],GPIO.LOW)
            x +=1
        time.sleep(0.03)
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


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
##  Relay Related Functions
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

############################################################################################################
# Turn off Relay
############################################################################################################
def TurnRelayOff() :

    GPIO.output(GPIO_relay_1,GPIO.LOW)

############################################################################################################
# Turn On Relay
############################################################################################################
def TurnRelayOn() :

    GPIO.output(GPIO_relay_1,GPIO.HIGH)

############################################################################################################
# Turn On Relay
############################################################################################################
def PulseRelay(duration) :

    GPIO.output(GPIO_relay_1,GPIO.HIGH)
    sleep(duration)
    GPIO.output(GPIO_relay_1,GPIO.LOW)

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# Functions related to RFID Pad and Registering Youth
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

############################################################################################################
## Read RFID Card and return back pipe delimited view of what is on the card. 
############################################################################################################
def ReadCard(CardData):
    print("\n Place RFID tag on PAD")
    CardData = ""
    OldText = ""
    while True:             ## Read ID off of car
        status,TagType = reader.read_no_block()
        # print(status)
        if status == 'None':
            ## only print "No Car Found" Once
            if NoCarFlag == 'N':
                print ("No Car Found")
            NoCarFlag = 'Y'        
        elif status != 'None':
            id,text = reader.read()
            if text != OldText:
                print(str(id) + "\n" + text + "\n")
                OldText=text
                CardData = str(id) + "|" + text
                NoCarFlag = 'N'
                break;
            else:
                print ("Same car")
            ## End If
        ## End If    
    ## End while loop waiting for card
    return CardData
## End def ReadCard()

############################################################################################################
## Read RFID Card and return back RFID only
############################################################################################################
def ReadRFIDCard(CardData):
    ## Read only RFID off of card
    print("\n Place RFID tag on PAD")
    CardData = ""
    OldText = ""
    while True:             ## Read ID off of car
        status,TagType = reader.read_no_block()
        # print(status)
        if status == 'None':
            ## only print "No Car Found" Once
            if NoCarFlag == 'N':
                print ("No Car Found")
            NoCarFlag = 'Y'        
        elif status != 'None':
            id,text = reader.read()
            if text != OldText:
                print(str(id) + "\n" + text + "\n")
                OldText=text
                CardData = str(id) 
                NoCarFlag = 'N'
                break;
            else:
                print ("Same car")
            ## End If
        ## End If    
    ## End while loop waiting for card
    return CardData
## End def ReadCard()


############################################################################################################
## Register a new racer (Update card and Database) 
############################################################################################################
def RegisterRacer(CardData):
## Register a New Racer

    cursor = db.cursor(buffered=True)
    RFCardID = ReadRFIDCard( CardData )  
  
    print(RFCardID)
    
    ## At this point you should have a valid ID off of the card. 

    CarName = input('Car Name: ')
    RacerFirstName = input('Racer First Name: ')
    RacerLastName = input('Racer Last Name: ')
        
    ## Check if this RFID is already in Use in the Database
    sql = "SELECT RacerID, RacerFirstName, RacerLastName, RacerPack,RacerCarName, RacerCarClass from RacerInfo WHERE RacerRFID= '"+ str(RFCardID) + "';"
    cursor.execute(sql)
    result = cursor.fetchone()

    if cursor.rowcount >= 1:
        print("RF ID Already Registered " + str(result[0]) + " "+ str(result[1]) + " " + str(result[2]) + " " + str(RFCardID) )
    else:
        ## RFID not already registered in the database so you can use it
        ## Write to the RFID Card the CarName and Racers Name
        reader.write(CarName + '|' + RacerFirstName + '|' + RacerLastName)
        print("Written")
    
        ## Now update the database 
        cursor = db.cursor()
        sql = "INSERT INTO racerinfo( RacerCarName, RacerFirstName, RacerLastName, RacerRFID) VALUES (%s, %s, %s, %s)" 
        print(str(RFCardID))
        val = (CarName, RacerFirstName, RacerLastName, str(RFCardID))
        cursor.execute(sql, val)
        db.commit()
        
        ## Verify that the insert worked
        sql = "SELECT RacerID, RacerFirstName, RacerLastName, RacerPack,RacerCarName, RacerCarClass from RacerInfo WHERE RacerRFID= '"+ RFCardID + "';"
        cursor.execute(sql)
        result = cursor.fetchone()

        if cursor.rowcount >= 1:
            print("Welcome " + str(result[0]) + " "+ result[1] + " " + result[2] )
            print("Remove Car from PAD")
        else:
            print("User does not exist, something went wrong!")
        ## End if
    ## End if
## End RegisterRacer

############################################################################################################
## This routine will replace RFID in RacerInfo with a new RFID and will update all records in RaceResults that had old RFID with the new RFID.
## This routine will get used when a car has lost its RFID tag and a new one is needed.
############################################################################################################
def LostRFIDCard():
## This routine will replace RFID in RacerInfo with a new RFID and will update all records in RaceResults that had old RFID with the new RFID.
## This routine will get used when a car has lost its RFID tag and a new one is needed.

    ## Get RFID from new tag
    NewRFID = readRFIDCard('False')
    
    ## print(NewRFID['RacerRFID'])
    
    ## Check if RFID is already in use
    sql = "SELECT * from racerinfo WHERE RacerRFID = '" + NewRFID['RacerRFID'] + "';" 
    
    cursor = db.cursor(buffered=True)
    cursor.execute(sql)
    
    result = []
    columns = tuple( [d[0] for d in cursor.description] )
    for row in cursor:
        result.append(dict(zip(columns, row)))
    
    cursor.close()
    pprint( result )
    xx = input("Do you wish to overwrite this card Y/N: ")
    ## Ask if you want to overwrite the card
    if xx == 'Y' or xx == 'y' :
        cursor = db.cursor(buffered=True)
        ## lookup database record
        ExistingRacer = lookupDBRacer()
        pprint( ExistingRacer )
        details = ExistingRacer[0]
        Racer = details['RacerID']
        sql = "UPDATE racerinfo SET RacerRFID = '" + str(NewRFID['RacerRFID']) + "' WHERE RacerID ='"+ str(Racer) + "';"
        cursor.execute(sql)
        sql = "UPDATE raceresults SET RacerRFID = '" + str(NewRFID['RacerRFID']) + "' WHERE RacerID ='"+ str(Racer) + "';"
        cursor.execute(sql)
        cursor.close()
        reader.write(str(details['RacerCarName']) + '|' + str(details['RacerFirstName']) + '|' + str(details['RacerLastName']))
        print("Written")
    
    ## End if check that card is to be overwritten

## End LostRFIDCard    


############################################################################################################
## Lookup racer record in the database.
## as there may be multiple records returns a list of dictionaries for all results found.
## if display = true then print results, otherwise just return results
## Can pass RacerID, RFID or will prompt for firstname / lastname 
############################################################################################################
def lookupDBRacer(display = 'True', **kwargs):
## Function to lookup a racer returns a list of dictionaries.
## if display = true then print results, otherwise just return results 
    if 'RacerRFID' in kwargs :
        sql = "SELECT RacerID, RacerFirstName, RacerLastName, RacerPack,RacerCarName, RacerRFID from RacerInfo WHERE RacerRFID= '"+ kwargs['RacerRFID'] + "';"
    elif 'RacerID' in kwargs :
        sql = "SELECT RacerID, RacerFirstName, RacerLastName, RacerPack,RacerCarName, RacerRFID from RacerInfo WHERE RacerID= '"+ kwargs['RacerID'] + "';"
    else :
        RacerFirstName = input('Racer First Name: ')
        RacerLastName = input('Racer Last Name: ')
        sql = "SELECT RacerID, RacerFirstName, RacerLastName, RacerPack,RacerCarName, RacerRFID from RacerInfo WHERE RacerFirstName= '"+ RacerFirstName + "' AND RacerLastName= '"+ RacerLastName + "';"
    ## end if kwargs
    
    cursor = db.cursor(buffered=True)
        
    ## Check if this Racer is Registered in the Database
    cursor.execute(sql)
    result = []
    columns = tuple( [d[0] for d in cursor.description] )
    for row in cursor:
        result.append(dict(zip(columns, row)))
    
    cursor.close()
    
    if display == 'True':
        pprint( result )
    ## end if
    return result
## end lookupDBRacer


############################################################################################################
## Read only RFID off the card
## if display = true then print results, otherwise just return results
## returns a dictionary of the card
############################################################################################################
def readRFIDCard(display = 'True'):
    ## Read only RFID off of card
    ## if display == true then print data, otherwise just return data
    print("\n Place RFID tag on PAD")
    CardData = ""
    OldText = ""
    while True:             ## Read ID off of car
        status,TagType = reader.read_no_block()
        # print(status)
        if status == 'None':
            ## only print "No Car Found" Once
            if NoCarFlag == 'N':
                print ("No Car Found")
            NoCarFlag = 'Y'        
        elif status != 'None':
            id,text = reader.read()
            if text != OldText:
                if display == 'True':
                    print(str(id) + "\n" + text + "\n")
                ## End if
                OldText=text            
                CardData = { 'RacerRFID' : str(id), 'cardtext' : text  }
                NoCarFlag = 'N'
                break;
            else:
                print ("Same car")
            ## End If
        ## End If    
    ## End while loop waiting for card
    return CardData
## End def ReadCard()

############################################################################################################
## Full roster of all racers in the database.
## as there may be multiple records returns a list of dictionaries for all results found.
## if display = true then print results, otherwise just return results 
############################################################################################################   
def RacerRoster(display = 'True'):
    ## Revised Function to lookup a racer returns a list of dictionaries (One dictionary for each racer) 
    sql = "SELECT RacerID, RacerFirstName, RacerLastName, RacerPack,RacerCarName, RacerRFID from RacerInfo;"
    cursor = db.cursor(buffered=True)
        
    ## Check if this Racer is Registered in the Database
     ## print(sql)
    cursor.execute(sql)

    result = []
    columns = tuple( [d[0] for d in cursor.description] )
    for row in cursor:
        result.append(dict(zip(columns, row)))
    
    cursor.close()
    
    if display == 'True':
        pprint( result )
    ## end if show results or just return results
    
    return result
############################################################################################################
## Lookup Database Record based on RFID card on the reader.
## as there may be multiple records returns a list of dictionaries for all results found.
## if display = true then print results, otherwise just return results
############################################################################################################   
def FullLookup(display = 'True') :
    results = readRFIDCard(display)
    
    racerResults = lookupDBRacer('False', **results)
    if display == 'True' :
        pprint(results)
        pprint( racerResults )
    ## end if should display results    
    return racerResults

## end FullLookup


############################################################################################################
## create a dictionary for a new racer
## Note:  RacerDict is a misnomer, it is actually a LIST containing a DICT
############################################################################################################
def createRacer(display = "True", **kwargs):
    
    ## AppendList = { 'lane' : kwargs['lane'] }
    print("Put Car on Pad")
    RacerDict = []
    while 1:
        RacerDict=FullLookup(display)
        if len(RacerDict) == 0:  ## list is empty
            print(" RFID Not Found " )
            flashLEDS()          ## indicate that there is an error
        else:
            break   ## break out of while loop
        ## end if list from FullLookup is empty
    
    ## end while
           
    ## if 'lane' in kwargs :
        ## print("Lane :", kwargs['lane'])
    ##    AppendList = {'lane' : kwargs['lane']}
    ##    RacerDict.update(AppendList)
    if display == 'True':    
        pprint(RacerDict)
    ## end if display == True
    return RacerDict



############################################################################################################
## Lookup Race Statistics - RaceCounter, FastestTime, Fastest Lane etc.
## if display = true then print results, otherwise just return results
## Can pass Unit #, or will just lookup maxRacecounter if none specified 
############################################################################################################
## Note: If there are no records in raceresults or track heat for the specified unit this routines just 
## hangs!!!  -- BUG!!
############################################################################################################
def lookupRaceStats(display = 'True', **kwargs):
## Function to lookup RaceCounter
## if display = true then print results, otherwise just return results 
    if 'Unit' in kwargs :
        # sql = "SELECT MAX(RaceCounter), MAX(Heat), MIN(RaceTime) from RaceResults WHERE Unit= '"+ str(kwargs['Unit']) + "';"
        sql = "SELECT MAX(A.RaceCounter) AS RaceCounter, RIGHT( MIN(A.RaceTime), 9) AS RaceTime, B.Heat FROM raceresults A INNER JOIN	trackheat B	ON A.Unit = B.TrackID WHERE A.Unit = '"+ str(kwargs['Unit']) + "' AND A.RaceTime > 00 ;"
    
    else :
        sql = "SELECT MAX(RaceCounter) As RaceCounter from RaceResults ;"
    ## end if kwargs
    
    cursor = db.cursor(buffered=True)
        
    ## Return race statistics in a list of dictionaries. (Should only be 1 row)
    cursor.execute(sql)
    
    result = []
    
    if cursor.rowcount >= 1:
    
        columns = tuple( [d[0] for d in cursor.description] )
    
        for row in cursor:
            result.append(dict(zip(columns, row)))
    
        cursor.close()

    else:
        print("No Data in RaceResults / Raceheat")
        result.append( { 'RaceCounter' : '1', 'RaceTime' : '0', 'Heat' : '1' } )
    
    ## end if check if there are records in the result set
    
    if display == 'True':
        pprint( result )
    ## end if
    return result
## end lookupRaceStats


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
##  End Functions -----------------------------------------------------------------------------------------
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

############################################################################################################
## Setup the GPIO's states
############################################################################################################
GPIO.setwarnings(False)
GPIO.setmode (GPIO.BOARD)                                       ## Use GPIO PIN #'s instead of GPIO ID's.
GPIO.setup(LDRLaneOne,GPIO.IN,pull_up_down = GPIO.PUD_UP)
GPIO.setup(LDRLaneTwo,GPIO.IN,pull_up_down = GPIO.PUD_UP)
GPIO.setup(LDRLaneThree,GPIO.IN,pull_up_down = GPIO.PUD_UP)
GPIO.setup(TrackSwitch,GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(GPIO_relay_1,GPIO.OUT)                               ## Set Relay to be an OUT

############################################################################################################
## Setup Listener Events on the GPIO
############################################################################################################
GPIO.add_event_detect(LDRLaneOne, GPIO.RISING, bouncetime = track_switch_bounce_time)
GPIO.add_event_detect(LDRLaneTwo, GPIO.RISING, bouncetime = track_switch_bounce_time)
GPIO.add_event_detect(LDRLaneThree, GPIO.RISING, bouncetime = track_switch_bounce_time)
GPIO.setup(GPIO_car_select_switch,GPIO.IN,pull_up_down = GPIO.PUD_UP)

# GPIO.setup(GPIO_car_select_switch, GPIO.IN)                 ## As we want program to stop on car select process we dont want a regular event detect.
                                                            ## dont know why but this seems to work.
# GPIO.add_event_detect(GPIO_car_select_switch, GPIO.RISING)

############################################################################################################
## Firing up the GUI
############################################################################################################

root = Tk() #Makes the window
app=FullScreenApp(root)
root.wm_title("Race Day") #Makes the title that will appear in the top left
root.config(background = "#FFFFFF")

############################################################################################################
## configure a default font
############################################################################################################
myfont = tkFont.Font(family='Helvetica',size=20, weight = "bold")
myfont2 = tkFont.Font(family='Helvetica',size=12, weight = "bold")

############################################################################################################
## Left Frame and its contents
############################################################################################################
leftFrame = Frame(root, width=1, height = 1)
leftFrame.grid(row=0, column=0, padx=2, pady=2)

############################################################################################################
## Right Frame and its contents
############################################################################################################
rightFrame = Frame(root, width=1, height = 1, relief = RIDGE )
rightFrame.grid(row=0, column=1, padx=10, pady=10)

############################################################################################################
## Start filling the left frame
############################################################################################################
Label(leftFrame, text="Ready to Race", width = 20, font = myfont, relief = RIDGE ).grid(columnspan=2,row=0, column=0, padx=4, pady=2)

############################################################################################################
## Create Ready to Race circleCanvas
############################################################################################################
circleCanvas = Canvas(leftFrame, width=100, height=100, bg='white')
circleCanvas.grid(columnspan=2, row=1, column=0, padx=10, pady=2, sticky = N )

############################################################################################################
## Add Race counter
############################################################################################################
Label(leftFrame, text="Race Counter", width = 20, font = myfont, relief = RIDGE ).grid(columnspan=2, row=2, column=0, padx=2, pady=2)
RCounter = Text(leftFrame, width = 5, height = 1, takefocus=0, font=myfont2)
RCounter.grid(columnspan=2,row=3, column=0, padx=2, pady=8)

############################################################################################################
## Fastest Racer Today
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
## Labels on Right Frame
############################################################################################################
Label(rightFrame, text="Current Race", width = 20, font = myfont, relief = RIDGE).grid(columnspan=2, row=0, column=0, padx=2, pady=2)

RaceLog = Text(rightFrame, width = 30, height = 10, takefocus=0)
RaceLog.grid(columnspan=2,row=14, column=0, padx=2, pady=2)

############################################################################################################
## Create labels and inputs for the various Lanes
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
# btnFrame = Frame(rightFrame, width=30, height = 3,relief = RIDGE )
# btnFrame.grid(row=10, column=0, padx=10, pady=5, columnspan = 2)

# RedBtn = Button(btnFrame, text="Red", command=redCircle)
# RedBtn.grid(row=0, column=2, padx=10, pady=2)


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
##  Main Loop -----------------------------------------------------------------------------------------
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

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
    ## What heat are we in. Reset between heats via database
    global Heat
    global MatrixYN

    global RelayYN

    global id
    global CurrentLane

    global db
    
    ## db = mysql.connector.connect(
    ## host='"' + Host + '"',
    ## user='"' + User + '"',
    ## passwd='"' + passwd + '"',
    ## database='"' + database + '"'
    ## )

    ## temporary connection string as it doesn't work pulling out of the settings file.
    db = mysql.connector.connect(
    host="192.168.100.148",
    ## host="localhost",
    user="cubcaradmin",
    passwd="cubsrock",
    database="CubCar"
    )

    cursor = db.cursor(buffered=True) ## for Database Interactions
    
    if LoadRFPAD == "true" :
        ## lookup race statistics out of the database 
        UnitDetails = { 'Unit' : Unit }
        RaceStats =  lookupRaceStats( 'True', **UnitDetails )
        details = RaceStats[0]
        RaceCounter = details['RaceCounter']
        Heat = details['Heat']
    ## end if 
    
    ## Start the Loop
    while 1:

        ## should really be using lists and arrays instead of individual variables
        Lane1Name = ""
        Lane2Name = ""
        Lane3Name = ""
        
        Lane1CarID = ""
        Lane2CarID = ""
        Lane3CarID = ""
        
        Lane1CarName = ""
        Lane2CarName = ""
        Lande3CarName = ""
        
        Lane1FirstName = ""
        Lane2FirstName = ""
        Lane3FirstName = ""
        
        Lane1LastName = ""
        Lane2LastName = ""
        Lane3LastName = ""
        
        Lane1Pack = ""
        Lane2Pack = ""
        Lane3Pack = ""
        
        Lane1RFID = ""
        Lane2RFID = ""
        Lane3RFID = ""
        
        RaceCounter +=1  # Increment Race Counter
        RCounter.delete(1.0, END)  #Clear out Race Counter on the GUI
        Msg = " " + str(RaceCounter)
        RCounter.insert(0.0, Msg)
    
        LastCarRFID = ""
        
        print ("Press start Button")
        RaceLog.insert(0.0, "Press Start\n")
        redCircle()
        root.update()

        if MatrixYN == 'Y':
            msg = "Let's Race!!!!"
            show_message(device, msg, fill="white", font=proportional(CP437_FONT), scroll_delay=0.05)
        ## End if using Matrix

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

        ## All the code for the RFID PAD goes here.
        if LoadRFPAD == "true" :
            CurrentLane = 1
            yelCircle()
            RaceLog.insert(0.0, "Load RF Pad\n")
            root.update()
            while CurrentLane <= 3 :
                details = {
                'lane' : CurrentLane 
                }
                RacerList = createRacer("True", **details)
                details = RacerList[0]
                if str(LastCarRFID) == str(details['RacerRFID']):
                    print("Same Car!!")
                    RaceLog.insert(0.0, "Same Car!!\n")
                    root.update()
                    flashLEDS()
                else:
                    RacerFirstName = details['RacerFirstName']
                    LastCarRFID = str(details['RacerRFID'])
                    print("Welcome " + RacerFirstName)
                    LightLEDBank(CurrentLane)
                    # root.update()
                    
                    ## Put Car on Track and push Button 1 on PAD
                    print("Put Car on Highlighted Lane")
                    
                    if CurrentLane == 1 :
                        Lane1CarID = details['RacerID']
                        Lane1CarName = details['RacerCarName']
                        Lane1FirstName = details['RacerFirstName']
                        Lane1LastName = details['RacerLastName']
                        Lane1Pack = details['RacerPack']
                        Lane1RFID = details['RacerRFID']
                        LLane1.delete(1.0, END)			# post to GUI
                        LLane1.insert(0.0, "Welcome " + RacerFirstName )
                    elif CurrentLane == 2:
                        Lane2CarID = details['RacerID']
                        Lane2CarName = details['RacerCarName']
                        Lane2FirstName = details['RacerFirstName']
                        Lane2LastName = details['RacerLastName']
                        Lane2Pack = details['RacerPack']
                        Lane2RFID = details['RacerRFID']
                        LLane2.delete(1.0, END)			# post to GUI
                        LLane2.insert(0.0, "Welcome " + RacerFirstName )
                    elif CurrentLane == 3:
                        Lane3CarID = details['RacerID']
                        Lane3CarName = details['RacerCarName']
                        Lane3FirstName = details['RacerFirstName']
                        Lane3LastName = details['RacerLastName']
                        Lane3Pack = details['RacerPack']
                        Lane3RFID = details['RacerRFID']
                        LLane3.delete(1.0, END)			# post to GUI
                        LLane3.insert(0.0, "Welcome " + RacerFirstName )
                    ## End if check for what lane you are in.
                    
                    root.update()
                
                    CurrentLane +=1
                    
                    
                    ## Now wait for car select button Push
                    ## print("Waiting for Button 1 to get pushed")
                    GPIO.wait_for_edge(GPIO_car_select_switch, GPIO.RISING, bouncetime = car_select_bounce_time )
                    ##  print("Button 1 pushed")
                ## End if This is same car on the pad
                
                resetLEDS()
            
            ## end while loop through tracks
        
        ## End of IF for RFPAD
        
        LLane1.delete(1.0, END)
        LLane2.delete(1.0, END)
        LLane3.delete(1.0, END)
        root.update()
        
        ## After all the cars have been loaded and recorded then wait for the start button.
        # wait for start button to be released
        print ("Release start Button")
        RaceLog.insert(0.0, "Release Start\n")
        grnCircle()
        root.update()
        if RelayYN == "Y":
            time.sleep(1)
            RaceLog.insert(0.0, "Racers Away - Relay\n")
            root.update()
            TurnRelayOn()
        else :
            GPIO.wait_for_edge(TrackSwitch, GPIO.RISING, bouncetime = TrackBounceTime)
            RaceLog.insert(0.0, "Racers Away - Switch\n")
            root.update()
        ## end if RelayYN
        
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

        # Capture Race start time
        StartTime = time.time()

        Lane1Place = 0                          # Needed for Database
        Lane2Place = 0                          # Needed for database
        Lane3Place = 0                          # Needed for Database

        Lane1Time = 0
        Lane2Time = 0
        Lane3Time = 0

        FirstPlace = 0  						# What lane ended up in first Place
        SecondPlace = 0 						# What lane ended up in Second Place
        ThirdPlace = 0  						# What lane ended up in Third Place
        LDRLaneOneFinishTime = 0 					# Time when Lane 1 Finished Race
        LDRLaneTwoFinishTime  = 0 					# Time when Lane 2 Finished Race
        LDRLaneThreeFinishTime = 0 				# Time When Lane 3 Finished Race
        Finishers = 0  							# Count of how many cars have completed the Race
        ident = " + "
        GFastestRaceIndicator = 0				# Indicator that a new fastest time has happened
        Msg1 = Lane1CarName + "\n  Lane 1  -  DNF"				# Set lanes to DNF as a default
        Msg2 = Lane2CarName +  "\n  Lane 2  -  DNF"				# Set lanes to DNF as a default
        Msg3 = Lane3CarName + "\n  Lane 3  -  DNF"				# Set lanes to DNF as a default

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
                        if LoadRFPAD == "true" :
                            Msg1 = Lane1Name + str(diff_time)[0:7]
                            print(Msg1)
                        else :
                            Msg1 = "Lane 1  -  " + str(diff_time)[0:7]
                            print(Msg1)
                        ## end if RFPAD
                        
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
                        ## End if what place gets assigned to lane 1 finish
                    ## end if no time for lane 1 already recorded
                ## end if check for short race         
            ## end if lane 1 event detected
            
            if GPIO.event_detected( LDRLaneTwo ):
                if ( time.time() - StartTime ) > ShortRaceTime:
                    if LDRLaneTwoFinishTime == 0:
                        LDRLaneTwoFinishTime = time.time()
                        Finishers +=1
                        diff_time = (LDRLaneTwoFinishTime - StartTime)
                        Lane2Time = str(diff_time)
                        if LoadRFPAD == "true" :
                            Msg2 = Lane2Name + str(diff_time)[0:7]
                            print(Msg2)
                        else :
                            Msg1 = "Lane 2  -  " + str(diff_time)[0:7]
                            print(Msg2)
                        ## end if RFPAD
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
                        ## end if what place has not been taken
                    ## end if no time for lane2 has been recorded
                ## end if check for short race time
            ## end if check for lane2 event detected    
            
            if GPIO.event_detected( LDRLaneThree ):
                if ( time.time() - StartTime ) > ShortRaceTime:
                    if LDRLaneThreeFinishTime == 0:
                        LDRLaneThreeFinishTime = time.time()
                        Finishers +=1
                        diff_time = (LDRLaneThreeFinishTime - StartTime)
                        Lane3Time = str(diff_time)
                        if LoadRFPAD == "true" :
                            Msg3 = Lane1Name + str(diff_time)[0:7]
                            print(Msg3)
                        else :
                            Msg3 = "Lane 3  -  " + str(diff_time)[0:7]
                            print(Msg3)
                        ## end if RFPAD
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
                        ## end If 
                    ## end if no lane finish time recorded
                ## end if check for short race 
            ## end if Lane3 event        
        ## end while have not timed out, all 3 racers have not finished
        
        ## update the screen
        root.update()

        # If all 3 racers have finished print stats
        Msg = str(FirstPlace) + " " + str(SecondPlace) + " " + str(ThirdPlace)
        print(Msg)

        if LoadRFPAD == "true" :
            ## Insert into Database
            sql = "INSERT INTO raceresults( RaceCounter, Unit, Heat, Lane, RacerID, CarName, RacerFirstName, RacerLastName, Pack, RaceTime, Placing, RacerRFID ) VALUES(%s, %s, %s, %s, %s, %s, %s ,%s, %s, %s, %s, %s)"
            val = (str(RaceCounter), str(Unit), str(Heat), '1', str(Lane1CarID), Lane1CarName, Lane1FirstName, Lane1LastName, str(Lane1Pack), str(Lane1Time), str(Lane1Place), str(Lane1RFID) )
            ## print(sql)
            ## print(val)
            
            cursor.execute(sql, val )
            db.commit()

            sql2 = "INSERT INTO raceresults( RaceCounter, Unit, Heat, Lane, RacerID, CarName, RacerFirstName, RacerLastName, Pack, RaceTime, Placing, RacerRFID ) VALUES(%s, %s, %s, %s, %s, %s, %s ,%s, %s, %s, %s, %s)"
            val2 = (str(RaceCounter), str(Unit), str(Heat), '2', str(Lane2CarID), Lane2CarName, Lane2FirstName, Lane2LastName, str(Lane2Pack), str(Lane2Time), str(Lane2Place), str(Lane2RFID) )
            ## print(sql2)
            ## print(val2)
            
            cursor.execute(sql2, val2 )
            db.commit()

            sql3 = "INSERT INTO raceresults( RaceCounter, Unit, Heat, Lane, RacerID, CarName, RacerFirstName, RacerLastName, Pack, RaceTime, Placing, RacerRFID ) VALUES(%s, %s, %s, %s, %s, %s, %s ,%s, %s, %s, %s, %s)"
            val3 = (str(RaceCounter), str(Unit), str(Heat), '3', str(Lane3CarID), Lane3CarName, Lane3FirstName, Lane3LastName, str(Lane3Pack), str(Lane3Time), str(Lane3Place), str(Lane3RFID) )
            ## print(sql3)
            ## print(val3)
            
            cursor.execute(sql3, val3 )
            db.commit()
            
        ## end if LoadRFPAD == True

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
            ## update_setting does not work in python 3, causes the settings file to blank!
            # update_setting(path, "Races", "GFastestLane", str(GFastestLane))
            # update_setting(path, "Races", "GFastestRaceCounter", str(RaceCounter))
            # update_setting(path, "Races", "GFastestTime", str(GFastestTime))
        ## End If Fastest Race Indicator
    
        if RelayYN == "Y":
            TurnRelayOff()
        ## end if RelayYN
       
    ## end while 1 loop
    
root.after(200, my_mainloop)

############################################################################################################
## Start the GUI and Run the Main Loop
############################################################################################################

try:
    resetLEDS()
    TurnRelayOff()
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

