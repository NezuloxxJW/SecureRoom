import nfc
import sqlite3
import uuid
import bcrypt
from datetime import datetime, timedelta
import time

uid = None
conn = sqlite3.connect('reservations.db',check_same_thread=False) 
cursor = conn.cursor()

def on_tag_connect(tag):
    global uid
    uid = tag.identifier.hex()
    print(uid)
    return True

def get_user_input():
    username = input("Entrez votre nom d'utilisateur : ")
    password = input("Entrez votre mot de passe : ")
    email = "test@test.com"
    return username, password, email

def main_register():
    global uid
    username, password, email = get_user_input()  # Récupère les informations de l'utilisateur
    
    with nfc.ContactlessFrontend('usb') as clf:
        clf.connect(rdwr={'on-connect': on_tag_connect})  # Attendre un scan de tag NFC
        
    try:
        print(password)
        hashed_pass = bcrypt.hashpw(password.encode('utf-8'),bcrypt.gensalt())
        print(hashed_pass)
        cursor.execute("INSERT INTO users (card_UID, token, mail, username, password) VALUES (?, ?, ?, ?, ?)", (uid, uuid.uuid4().hex, email, username, hashed_pass))
        conn.commit()
        print("added")
        return True
    except: return False

def printusers():
    cursor.execute("SELECT * FROM users ")
    fetched = cursor.fetchall()
    print(fetched)
    
def deleteuser(id):
    cursor.execute(f"DELETE FROM users WHERE id = {int(id)}")
    conn.commit()

def fetch_user_token_from_card(uid):
    cursor.execute("SELECT token FROM users WHERE card_uid=?", (uid,))
    token = cursor.fetchone()
    return token[0] if token else None

def get_date_time():
    now = datetime.now()
    current_date = now.strftime("%Y-%m-%d")  # Format: AAAA-MM-JJ
    current_time = now.strftime("%H:%M") 
    return current_date, current_time

def verifyTime(scanTime, reservationTime, reservationDuration):
    # Convertir les chaînes en objets datetime si nécessaire
    scanTime = datetime.strptime(scanTime, "%H:%M")
    reservationTime = datetime.strptime(reservationTime, "%H:%M")
    reservationDuration = timedelta(hours=int(reservationDuration.split(':')[0]), minutes=int(reservationDuration.split(':')[1]))

    # Calculer l'heure de fin de réservation
    endTime = reservationTime + reservationDuration

    # Vérifier si scanTime est entre reservationTime et endTime
    return reservationTime <= scanTime <= endTime

def fetch_reservation_from_card(uid, time, date):
    token = fetch_user_token_from_card(uid)
    print(token)
    if not token:
        return False
    
    cursor.execute("SELECT time, duration FROM reservations WHERE user_token=? AND date=?", (token, date))
    reservations = cursor.fetchall()
    for reservation in reservations:
        reservationTime = reservation[0]
        reservationDuration = reservation[1]

        if(verifyTime(time, reservationTime, reservationDuration)):
            print(f"Réservation {reservationTime} pendant {reservationDuration} le {date} disponible")
            return True

    return False    

def on_tag_connect_door(tag):
    uid = tag.identifier.hex()
    date, time = get_date_time()
    print(date)
    print(time)

    if fetch_reservation_from_card(uid, time, date):
        return True
    else:
        print("Aucune réservation disponible.")
        return False
        
def main_door():
    with nfc.ContactlessFrontend('usb') as clf:
        clf.connect(rdwr={'on-connect': on_tag_connect_door})


def main():
    choice = input("1 = print, 2 = register, 3 = del, 4 = check : ")
    if choice == "1": printusers()
    if choice == "2": main_register()
    if choice == "3": 
        id = input("which id ? ") 
        deleteuser(id)
    if choice == "4": main_door()
    if choice == "5":
        i = 0
        while i < 60:
            main_door()
            i += 1
            time.sleep(1)
    
    
main()
