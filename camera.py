import RPi.GPIO as GPIO		#Nodig voor het gebruiken van het breadboard
import subprocess		#Nodig voor het gebruiken van shell commands die niet in python kunnen
import time			#Nodig voor het gebruiken van sleep
from threading import Timer	#Nodig voor het gebruiken van een klok van een half uur
import pymysql

def Start_camera():
	subprocess.Popen(["sh", "/home/pi/camera_start.sh"])	#Roept een shell script aan om de camera te starten
	global Camera_status					#Vraagt de status van de camera op
	Camera_status = 1					#Zet de status op aan
	Timer.cancel						#Stopt de timer van een half uur
def Light():
	global cur
	global connection
	global light_status		#Vraagt de status van de lichten op
	if light_status == 0:	#Als het licht uit staat
		print ('lamp gaat aan')
#		GPIO.output(5, True)	#De lamp gaat aan
		cur.execute ("UPDATE status SET verlichting='1' WHERE bewonerID='1'")
#		light_status = True	#Status van het licht staat ook op aan
	elif light_status == 1:	#Maar als de lichten aan staan
		print('lamp gaat uit')
#		GPIO.output(5, False)	#Het licht gaat uit
		cur.execute ("UPDATE status SET verlichting='0' WHERE bewonerID='1'")
#		light_status = False	#Status van het licht staat ook uit
	print('voor commit')
	time.sleep(1)
	connection.commit()
	print('light')
def switch_light():
	global light_status
	if light_status == 0:
		GPIO.output(5, True)
	elif light_status == 1:
		GPIO.output(5, False)
def Camera():
	global Camera_status                                              #Vraat de status van de camera op
	global cur
	global connection
	if Camera_status == 1:					#Als de camera aan staat
#		subprocess.Popen(["sh", "/home/pi/camera_stop.sh"])	#Roept een shell script aan om de camera te stoppen
		cur.execute ("UPDATE status SET camera='1' WHERE bewonerID='1'")
#		Camera_status = False					#STatus van de camera gaat uit
		Timer(1800.0,Start_camera).start()			#Hier begint een timer van 30 minuuten
		print('camera gata uit')
#		time.sleep(1)						#1 seconde sleep zodat de lamp niet gelijk weer uitgaat als je iets te lang o de knop drukt
	elif Camera_status == 0:					#Als de lamp uit staat
#		Start_camera()
#		Camera_status = True
		print('camera gaat aan')
		cur.execute ("UPDATE status SET camera='0' WHERE bewonerID='1'")
	print('voor commit')
	connection.commit()
	time.sleep(1)
	print('camera')							#1 seconde sleep zodat alles de tijd heeft om aan/uit te gaan
def switch_camera():
	global Camera_status                                            #Vraat de status van de camera op
	if Camera_status == 1:                                       #Als de camera aan staat
		subprocess.Popen(["sh", "/home/pi/camera_stop.sh"])     #Roept een shell script aan om de camera te stoppen
#		Camera_status = False
	elif Camera_status == 0:
        	subprocess.Popen(["sh", "/home/pi/camera_start.sh"])    #Roept een shell script aan om de camera te starten
 #       	Camera_status = True                                    #Zet de status op aan
        	Timer.cancel                                            #Stopt de timer van een half uur
def Alarm():
	print ('Alarm')
	global light_status	#Vraagt de status van het licht op
	light_status = 0	#Zet de status op uit zodat de lamp altijd aan gaat
	Light()
	global Camera_status		#Zorgt dat de lamp aangaat
	Camera_status = 0
	switch_camera		#De camera gaat aan
	sleep(1)		#Zodat het alarm niet 10 keer per seconde afgaat
def connect():
	global connection
	connection = pymysql.connect(host="145.89.160.88",port=3306,user="GROEP4",passwd="IDP",db="SJAAK")
	global cur
	cur = connection.cursor()
def loop():
	global light_status
	global Camera_status
	global cur
	if GPIO.input(7) == False:	#Als de gele knop word ingedrukt
		Camera()		#Begin de functie main_button waardoor de camera aan/uit gaat
		#value in database veranderen
	if GPIO.input(3) == False:	#Als de blauwe knop in word gedrukt
		Light()			#Gaat het licht aan of uit
		#value in database aanpassen
	if GPIO.input(11) == False:	#Als de rode knop in word gedrukt
		Alarm()			#Gaat het alarm af
		#value in database aanpassen
	cur.execute('SELECT camera, verlichting FROM status ''WHERE bewonerID = 1')
	sqldata = cur.fetchall()
	for row in sqldata:
		if light_status != row[1]:
			light_status = row[1]
			switch_light()
		if camera_status != row[0]:
			camera_status = row[0]
			switch_camera()

#		if row[1] == 1:
#			Temp1 = True
#		if row[1] == 0:
#			Temp1 = False
#		if row[0] == 1:
#			Temp2 = True
#		if row[0] == 0:
#			Temp2 = False
#		if Temp1 == True and Temp1 != light_status:
#			light_status = True
#			switch_light()
#		if Temp1 == False and Temp1 != lightstatus:
#			light_status = False
#			switch_light()
#		if Temp2 == True and Temp2 != camera_status:
#			camera_status = True
#			switch_camera()
#		if Temp2 == False and Temp2 != camera_status:
#			light_status = False
#			switch_camera()
	time.sleep(1)			#Hij checked 10 keer per seconde of er een knop in word gedrukt

GPIO.setwarnings(False)					#Stopt onnodige warnings
GPIO.setmode(GPIO.BOARD)				#Zorgt er voor dat de goede pins worden gebruikt op het breadboard
GPIO.setup(7, GPIO.IN, pull_up_down=GPIO.PUD_UP)	#Zorgt dat de gele knop afgelezen kan worden
GPIO.setup(5, GPIO.OUT)					#Zorgt dat het lampje aan en uit kan
GPIO.setup(3, GPIO.IN, pull_up_down=GPIO.PUD_UP)	#Zorgt dat de blauwe knop afgelezen kan worden
GPIO.setup(11, GPIO.IN, pull_up_down=GPIO.PUD_UP)	#Zorgt ervoor dat de rode knop afgelezen kan worden
light_status = False					#De status van het licht gaat uit
GPIO.output(5, GPIO.LOW)				#Het licht gaat uit
subprocess.Popen(["sh", "/home/pi/camera_start.sh"])	#Roept een sheel script aan om de camera te starten
Camera_status = True					#De status van de camera staat aan
subprocess.Popen(["sh", "/home/pi/cmraBeeldDel.sh"])	#Roept een shell script aan om onnodige beelden te verwijderen zodat de opslag van de PI niet vol raakt
connect()

try:
	while True:
		try:
						#Hierdoor blijft hij altijd doorgaan
			loop()
		except:
			connect()					#Zorgt er voor dat de knoppen worden gechecked op verandering
except KeyboardInterrupt:					#WIP in het uiteindelijke product gaat dit weg maar voor het POC is het nodig om testen uit te voeren
	Timer.cancel						#De timer van een half uur stopt
	subprocess.Popen(["sh", "/home/pi/camera_stop.sh"])	#Roept een shell script aan om de camera te stoppen
	GPIO.output(5, False)					#De lamp gaat weer uit
	cursor.close()
	connection.close()
