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
    return True

def get_user_input():
    username = input("Entrez votre nom d'utilisateur : ")
    password = input("Entrez votre mot de passe : ")
    email = input("Entrez votre email : ")
    return username, password, email

def main_register():
    global uid
    username, password, email = get_user_input()  # Récupère les informations de l'utilisateur
    
    with nfc.ContactlessFrontend('usb') as clf:
        clf.connect(rdwr={'on-connect': on_tag_connect})  # Attendre un scan de tag NFC
        
    try:
        hashed_pass = bcrypt.hashpw(password.encode('utf-8'),bcrypt.gensalt())
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



def main():
    choice = input("1 = print, 2 = register, 3 = del, 4 = check : ")
    if choice == "1": printusers()
    if choice == "2": main_register()
    if choice == "3": 
        id = input("which id ? ") 
        deleteuser(id)
    
    
main()
