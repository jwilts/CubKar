#file -- Registration.py --
#!/usr/bin/env python

############################################################################################################
##	Version: 1.0
##  Date: Jan 14/2020
##  This application utilizes an RC-522 RFID pad and a mariaDB database to do basic registration for 
##  cubcar races.  The program checks to see if the RFID is already in use in the database before creating'
##  a new record.   
##  
############################################################################################################
## Notes:
## 
##
###########################################################################################################

import time
import mysql.connector

import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522

reader = SimpleMFRC522()

## Connection String for Database
db = mysql.connector.connect(
    # host="localhost",
    host="localhost",
    user="root",
    passwd="bingo",
    database="CubCar"
)

OldText = ''                            ## Used to Check that the text on the card has changed
NoCarFlag = 'N'                         ## Used to only display message No Car Found once

try:
    While 1:
        CarName = input('Car Name:')
        RacerFirstName = input('Racer First Name:')
        RacerLastName = input('Racer Last Name:')
        print("Place RFID tag on PAD")
        while True:             ## Read ID off of car
            # time.sleep(0.25)
            try:
                status,TagType = reader.read_no_block()
                print(status)
                if status == 'None':
                    ## only print "No Car Found" Once
                    if NoCarFlag == 'N'
                        print ("No Car Found")
                    NoCarFlag = 'Y'        
                elif status != 'None':
                    id,text = reader.read()
                    if text != OldText:
                        print(id)
                        OldText=text
                        NoCarFlag = 'N'
                        break;
                    else:
                        print ("Same car")
                    ## End If
                ## End If
            ## End Try    
        ## End while loop waiting for card
        
        ## At this point you should have a valid ID off of the card. 
        
        ## Check if this RFID is already in Use in the Database
        sql = "SELECT ID, RacerFirstName, RacerLastName, RacerPack,RacerCarName, RacerCarClass from RacerInfo WHERE RacerRFID= "+ str(id) 
        cursor.execute(sql)
        result = cursor.fetchone()

        if cursor.rowcount >= 1:
            print("RF ID Already Registered " + str(result[0]) + " "+ result[1] + " " + result[2] + " " + id )
        else:
            ## RFID not already registered in the database so you can use it
            ## Write to the RFID Card the CarName and Racers Name
            reader.write(CarName + '|' + RacerFirstName + '|' + RacerLastName)
            print("Written")
		
            ## Now update the database 
            cursor = db.cursor()
            sql = "INSERT INTO racerinfo( RacerCarName, RacerFirstName, RacerLastName,RacerRFID) VALUES (%s, %s, %s, %s)"
        
            cursor.execute(sql, CarName, RacerFirstName, RacerLastName, id )
            db.commit()
            
            ## Verify that the insert worked
            sql = "SELECT ID, RacerFirstName, RacerLastName, RacerPack,RacerCarName, RacerCarClass from RacerInfo WHERE RacerRFID= "+ str(id) 
            cursor.execute(sql)
            result = cursor.fetchone()

            if cursor.rowcount >= 1:
                print("Welcome " + str(result[0]) + " "+ result[1] + " " + result[2] )
                print("Remove Car from PAD")
            else:
                print("User does not exist, something went wrong!")
            ## End if
        ## End if
    
    ## end while Loop
## End Try
    
finally:
        GPIO.cleanup()
## End Finally