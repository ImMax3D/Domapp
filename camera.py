import RPi.GPIO as GPIO		#Nodig voor het gebruiken van het breadboard
import subprocess		#Nodig voor het gebruiken van shell commands die niet in python kunnen
import time			#Nodig voor het gebruiken van sleep
from threading import Timer	#Nodig voor het gebruiken van een klok van een half uur
import pymysql			#Nodig voor het verbinden met de database

def Start_camera():
	global camera_status                                    		#Vraagt de status van de camera op
	global connection							#Dit is nodig voor het opslaan van de veranderingen in de database
	global cur								#Dit is nodig voor het updaten van de database
	subprocess.Popen(["sh", "/home/pi/camera_start.sh"])			#Roept een shell script aan om de camera te starten
	cur.execute ("UPDATE status SET camera='1' WHERE bewonerID='1'")	#Verandert de waarde in de database
	connection.commit()							#Zorgt ervoor dat de veranderingen worden opgeslagen in de database
	Timer.cancel								#Stopt de timer van een half uur
def Light():
	global cur									#Dit is nodig voor het updaten van de database
	global connection								#Dit is nodig voor het opslaan van de veranderingen in de database
	global light_status								#Vraagt de status van de lichten op
	if light_status == 0:								#Als het licht uit staat
		cur.execute ("UPDATE status SET verlichting='1' WHERE bewonerID='1'")	#Verandert de licht status in de database
	elif light_status == 1:								#Maar als de lichten aan staan
		cur.execute ("UPDATE status SET verlichting='0' WHERE bewonerID='1'")	#Verandert de licht status in de database
	time.sleep(1)									#1 seconde sleep zodat alles de tijd heeft om aan/uit te gaan
	connection.commit()								#Zorgt ervoor dat de veranderingen worden opgeslagen in de database
def switch_light():
	global light_status		#Vraag de status van het licht op
	if light_status == 0:		#Als het licht uit staat
		GPIO.output(5, True)	#Het licht gaat aan
	elif light_status == 1:		#Maar als de lichten aan staan
		GPIO.output(5, False)	#Het licht gaat uit
def Camera():
	global camera_status                                              		#Vraag de status van de camera op
	global cur									#Dit is nodig voor het updaten van de database
	global connection								#Dit is nodig voor het opslaan van de veranderingen in de database
	if camera_status == 1:								#Als de camera aan staat
		cur.execute ("UPDATE status SET camera='0' WHERE bewonerID='1'")	#Verandert de camera status in de database
		Timer(1800.0,Start_camera).start()					#Hier begint een timer van 30 minuuten om automatisch weer aan te gaan
	elif camera_status == 0:							#Als de lamp uit staat
		cur.execute ("UPDATE status SET camera='1' WHERE bewonerID='1'")	#Verander de camera status in de database
	connection.commit()								#Zorgt ervoor dat de veranderingen worden opgeslagen in de database
	time.sleep(1)									#1 seconde sleep zodat alles de tijd heeft om aan/uit te gaan
def switch_camera():
	global camera_status                         			#Vraat de status van de camera op
	if camera_status == 1:                                      	#Als de camera aan staat
		subprocess.Popen(["sh", "/home/pi/camera_stop.sh"])     #Roept een shell script aan om de camera te stoppen
	elif camera_status == 0:					#Als de camera uit staat
        	subprocess.Popen(["sh", "/home/pi/camera_start.sh"])    #Roept een shell script aan om de camera te starten
        	Timer.cancel                                            #Stopt de timer van een half uur
def Alarm():
	global cur								#Dit is nodig voor het updaten van de database
	global light_status							#Vraagt de status van de lichten op
	global camera_status							#Vraag de status van de camera op
	global connection							#Dit is nodig voor het opslaan van de veranderingen in de database
	cur.execute ("UPDATE status SET camera='1' WHERE bewonerID='1'")	#Verander de camera status in de database
	light_status = 1							#Zet de status op 1 zodat de lamp altijd aan gaat
	cur.execute ("UPDATE status SET verlichting='1' WHERE bewonerID='1'")   #Verandert de licht status in de database
	Light()									#Het licht gaat aan
	camera_status = 1							#Zet de status op 1 zodat de camera altijd aan gaat
	switch_camera()								#De camera gaat aan
	connection.commit()							#Zorgt ervoor dat de veranderingen worden opgeslagen in de database
	sleep(1)								#Zodat het alarm niet 10 keer per seconde afgaat
def connect():
	global connection											#Dit is nodig voor het opslaan van de veranderingen in de database
	connection = pymysql.connect(host="145.89.160.88",port=3306,user="GROEP4",passwd="IDP",db="SJAAK")	#Zorgt voor de verbinding tussen de database en de client pi
	global cur												#Dit is nodig voor het updaten van de database
	cur = connection.cursor()										#Zorgt dat de updates voor de database ook in ander functies uitgevoerd kunnen worden
def loop():
	global light_status								#Vraagt de status van de lichten op
	global camera_status								#Vraag de status van de camera op
	global cur									#Dit is nodig voor het updaten van de database
	if GPIO.input(7) == False:							#Als de gele knop word ingedrukt
		Camera()								#Gaat de camera aan/uit
	if GPIO.input(3) == False:							#Als de blauwe knop in word gedrukt
		Light()									#Gaat het licht aan of uit
	if GPIO.input(11) == False:							#Als de rode knop in word gedrukt
		Alarm()									#Gaat het alarm af
	cur.execute('SELECT camera, verlichting FROM status ''WHERE bewonerID = 1')	#Kijkt in de database bij de tabellen van huis 1
	sqldata = cur.fetchall()							#Maakt een bruikbare tabel van de waarden van camera en verlichting
	for row in sqldata:								#Kijkt per rij
		if light_status != row[1]:						#Als de status op de pi anders is dan op de database
			light_status = row[1]						#De database heeft prioriteit en geet dus de status aan
			switch_light()							#het licht gaat aan/uit
		if camera_status != row[0]:						#Als de status op de pi anders is dan op de database
			camera_status = row[0]						#De database heeft prioriteit en geet dus de status aan
			switch_camera()							#De camera gaat aan/uit
	time.sleep(0.1)									#Hij checked 10 keer per seconde of er een knop in word gedrukt

GPIO.setwarnings(False)					#Stopt onnodige warnings
GPIO.setmode(GPIO.BOARD)				#Zorgt er voor dat de goede pins worden gebruikt op het breadboard
GPIO.setup(7, GPIO.IN, pull_up_down=GPIO.PUD_UP)	#Zorgt dat de gele knop afgelezen kan worden
GPIO.setup(5, GPIO.OUT)					#Zorgt dat het lampje aan en uit kan
GPIO.setup(3, GPIO.IN, pull_up_down=GPIO.PUD_UP)	#Zorgt dat de blauwe knop afgelezen kan worden
GPIO.setup(11, GPIO.IN, pull_up_down=GPIO.PUD_UP)	#Zorgt ervoor dat de rode knop afgelezen kan worden
light_status = 0					#De status van het licht gaat uit
GPIO.output(5, GPIO.LOW)				#Het licht gaat uit
subprocess.Popen(["sh", "/home/pi/camera_start.sh"])	#Roept een shell script aan om de camera te starten
camera_status = 1					#De status van de camera staat aan
subprocess.Popen(["sh", "/home/pi/cmraBeeldDel.sh"])	#Roept een shell script aan om onnodige beelden te verwijderen zodat de opslag van de PI niet vol raakt
connect()						#Zorgt voor het verbinden met de database

try:
	while True:			#Dit blijft altijd doorgaan
		try:			#Probeert de standaard functie te gebruiken
			loop()		#Dit blijft altijd checken of er inputs zijn
		except:			#Als er geen verbinding is
			connect()	#Probeert opnieuw verbinding te maken
except KeyboardInterrupt:					#WIP in het uiteindelijke product gaat dit weg maar voor het POC is het nodig om testen uit te voeren
	Timer.cancel						#De timer van een half uur stopt
	subprocess.Popen(["sh", "/home/pi/camera_stop.sh"])	#Roept een shell script aan om de camera te stoppen
	GPIO.output(5, False)					#De lamp gaat weer uit
	cursor.close()						#De interactie met de database gaat uit
	connection.close()					#De verbinding gaat uit
