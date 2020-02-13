#file -- Registration.py --
#!/usr/bin/env python

############################################################################################################
##	Version: 1.1
##  Date: Feb 12/2020
##  This application utilizes an RC-522 RFID pad and a mariaDB database to do basic registration for 
##  cubcar races.  The program checks to see if the Youth and or RFID is already in use in the database 
##  before creating a shell of a record.   
##  
############################################################################################################
## Notes:  Will want to add a simple text menu to give choices - Register, Read Card, Update RFID
## 
##
###########################################################################################################

import time
import mysql.connector

import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
from pprint import pprint

import os

GPIO.setwarnings(False)
reader = SimpleMFRC522()

## Connection String for Database
db = mysql.connector.connect(
    host="192.168.0.137",
    ## host="localhost",
    user="cubcaradmin",
    passwd="cubsrock",
    database="CubCar"
)

OldText = ''                            ## Used to Check that the text on the card has changed
NoCarFlag = 'N'                         ## Used to only display message No Car Found once

MenuText = "1. Read RFID Card \n"
MenuText = MenuText + "2. Lookup Cub Record From Database \n"
MenuText = MenuText + "3. Register New Racer \n"
MenuText = MenuText + "4. Lost RFID Card \n"
MenuText = MenuText + "5. Update Heat \n"
MenuText = MenuText + "6. Update Racer information \n"
MenuText = MenuText + "7. Roster \n"
MenuText = MenuText + "8. Use RFID Lookup DB \n"
MenuText = MenuText + "9. Exit \n"

def Main():
    os.system('clear')  
    print( 30 * "-", "MENU", 30 * "-")
    print( MenuText)
    print( 67 * "-")
## end def Main()


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
## End def ReadRFIDCard()


############################################################################################################
## Register a new racer (Update card and Database) 
############################################################################################################
def RegisterRacer(CardData):
## Register a New Racer

    cursor = db.cursor(buffered=True)
    RFCardID = ReadRFIDCard( CardData )  
  
    print(RFCardID)
    
    ## At this point you should have a valid ID off of the card. 

    CarName = input('Car Name:')
    RacerFirstName = input('Racer First Name:')
    RacerLastName = input('Racer Last Name:')
        
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
## create a dictionary for a new racer
## INCOMPLETE
############################################################################################################
def createRacer(**kwargs):
    print("**********************")
    print("Creating Racer Dictionary")
    LTwo = { 'name' : 'Bear', 'carname' : 'Zippy', 'lane' : '1' }
    if 'lane' in kwargs :
        ## print("Lane :", kwargs['lane'])
        AppendList = {'lane' : kwargs['lane']}
        LTwo.update(AppendList)
    print(LTwo)
    return LTwo

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
        RacerFirstName = input('Racer First Name:')
        RacerLastName = input('Racer Last Name:')
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
## End def readRFIDCard()

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
## New Heat 
############################################################################################################
def NewHeat():
## Register a New Heat for a particular track

    cursor = db.cursor(buffered=True)
    Heat = input('Heat Number: ')
    Unit = input('Track ID : ')
           
    ## Delete any records for this given track  
    cursor = db.cursor()
    sql1 = "DELETE FROM TrackHeat WHERE TrackID = '" + str(Unit) + "';"
    cursor.execute(sql1)
    
    sql2 = "INSERT INTO TrackHeat( [Heat], [Unit]) VALUES (%s, %s)" 
    val2 = (Heat, Unit)
    cursor.execute(sql2, val2)
    db.commit()
    
    print("Restart Track timer to take effect!")
    
## End NewHeat


    
#########################################################################################################################################
## Begin Main part of the program
#########################################################################################################################################


while 1:
    ## racerinfo = createRacer()
    
    CardData = ""
    Main()
    xx = '0'
    xx = input("Enter Your Choice:")
    
    if xx == "9":
        break
    elif xx == "8":
        FullLookup('True')
        input("Press Enter")
    elif xx == "7":
        pprint(RacerRoster('False'))
        input("Press Enter")
    elif xx == "6":
        ## UpdateRacerInfo()
        input("Press Enter")
    elif xx == "5":
        NewHeat()
        input("Press Enter")
    elif xx == "4":
        LostRFIDCard()
        input("Press Enter")
    elif xx == "3":
        RegisterRacer(CardData)
        input("Press Enter")
    elif xx == "2":
        results = lookupDBRacer('False')
        pprint( results )
        input("Press Enter")
    elif xx == "1":
        results = readRFIDCard('True')
        pprint( results )
        input("Press Enter")
    else:
        print("I don't understand your choice.")  
    ## end if
       
## End While


