from datetime import datetime, timedelta
import os, sys, threading, time, nfc
from time import sleep


from debug import DbgPrint
from db import db
from door import door

bThreadRunning = True

# main du thread NFC
def ThreadNfc():
    with nfc.ContactlessFrontend('usb') as clf:
        while bThreadRunning:
            clf.connect(rdwr={'on-connect': nfcReader.onNfcRead})


threadNFC = threading.Thread(target=ThreadNfc)

# Lance le thread du lecteur NFC
def launchThreadNfc():
    threadNFC.start()

# Ferme le thread et quitte
def signal_handler(sig, frame):
    global bThreadRunning
    bThreadRunning = False

    DbgPrint("[!] Fermeture de l'application...")
    threadNFC.join(timeout=5)
    if threadNFC.is_alive():
        DbgPrint("[!!] Le thread NFC ne s'est pas arrêté, forçage de la sortie.", "red")
        os._exit(1)
    sys.exit(0)

class nfcReader:

    # Vérifie si l'heure de scan se trouve durant la réservation
    def verifyTime(scanTime, reservationTime, reservationDuration):
        scanTime = datetime.strptime(scanTime, "%H:%M")
        reservationTime = datetime.strptime(reservationTime, "%H:%M")
        reservationDuration = timedelta(hours=int(reservationDuration.split(':')[0]), minutes=int(reservationDuration.split(':')[1]))

        endTime = reservationTime + reservationDuration

        return reservationTime <= scanTime <= endTime


    # Récupere la réservation et verifie que ca soit la bonne
    def verifyReservationFromUID(uid, time, date):
        token = db.fetchTokenFromCardUid(uid)
        if not token:
            return False

        reservations = db.fetchReservationFromTokenDate(token,date)

        for reservation in reservations:
            reservationTime = reservation[0]
            reservationDuration = reservation[1]
            if(nfcReader.verifyTime(time, reservationTime, reservationDuration)):
                DbgPrint(f"[+] Réservation {reservationTime} pendant {reservationDuration} le {date} disponible", "green")
                return True
        return False  

    def onNfcRead(tag):
        DbgPrint("[*] NFC read", "yellow")
        # Récuperer l'ID de la carte
        uid = tag.identifier.hex()
        
        now = datetime.now()

        # Récuperer la date du jour et l'heure
        date = now.strftime("%Y-%m-%d")
        time = now.strftime("%H:%M") 

        if nfcReader.verifyReservationFromUID(uid, time, date):
            door.open()
            return True
        else:
            DbgPrint(f"[-] Aucune réservation disponible pour {date}, {time}.", "red")
            return False
