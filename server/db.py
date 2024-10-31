import sqlite3
from datetime import datetime
import bcrypt

from debug import DbgPrint

conn = sqlite3.connect('reservations.db',check_same_thread=False) 
cursor = conn.cursor()

class verify:
    # Vérification des chevauchement des reservations
    def verifyOverlap(submitTime,submitDuration, reservedTimes) -> bool:
        DbgPrint("[*] Start verifying overlaps", "yellow")
        submitHour = int(submitDuration.split(":")[0])
        submitMin = int(submitDuration.split(":")[1])
        submitEndTimeHour = int(submitTime.split(":")[0]) + submitHour
        submitEndTimeMin = int(submitTime.split(":")[1]) +  submitMin
        
        if submitEndTimeMin == 60: endSubmitTime = f"{submitEndTimeHour+1:02}:00"
        else: endSubmitTime = f"{submitEndTimeHour:02}:{submitEndTimeMin:02}"

        DbgPrint(f"[~] {submitTime} -> {endSubmitTime}")
        for reservation in reservedTimes:
            if reservation['end_time'].split(":")[1] == '60': endReservationTime = f"{int(reservation['end_time'].split(':')[0])+1:02}:00"
            else: endReservationTime = f"{reservation['end_time'].split(':')[0]:02}:{reservation['end_time'].split(':')[1]:02}"
            DbgPrint(f"[~] Already reserved : {reservation['time']} -> {endReservationTime}")
            debut1 = datetime.strptime(reservation['time'], '%H:%M')
            fin1 = datetime.strptime(endReservationTime, '%H:%M')
            debut2 = datetime.strptime(submitTime, '%H:%M')
            fin2 = datetime.strptime(endSubmitTime, '%H:%M')
            if debut2 < fin1 and fin2 > debut1: return False

        DbgPrint("[+] No overlaps exiting with success", "green")
        return True

    # Vérification des donnée recu.
    def verifySumbitDatas(date, time, duration, token, description) -> bool:
        # Vérification du bon format pour la date 
        DbgPrint("[*] Start verifying submit data", "yellow")

        try: datetime.strptime(date, "%Y-%m-%d")
        except:
            DbgPrint("[-] date invalid", "red")  
            return False

        DbgPrint("[+] date valid")

        # Vérification du bon format pour l'heure
        try: datetime.strptime(time, "%H:%M")
        except:
            DbgPrint("[-] time invalid", "red")  
            return False

        DbgPrint("[+] time valid")

        # Vérification que la durée est positif + integer
        try: datetime.strptime(duration, "%H:%M")
        except:
            DbgPrint("[-] duration invalid", "red") 
            return False

        DbgPrint("[+] duration valid")

        # Vérification que l'ID publique de la carte soit intégré a la DB
        if not db.checkTokenValid(token): return False
        DbgPrint("[+] token valid")

        if description is None: return False
        DbgPrint("[+] description valid")

        DbgPrint("[+] Exiting Data Verification with success", "green")
        return True

class format:
    # Formatage des reservations
    def formatReservations(reservations):
        formatted_reservations = []

        for reservation in reservations:
            time = reservation[0]
            duration = reservation[1]

            timeHour = int(duration.split(":")[0])
            timeMin = int(duration.split(":")[1])
            endTimeHour = int(time.split(":")[0]) + timeHour
            endTimeMin = int(time.split(":")[1]) +  timeMin

            endTime = f"{endTimeHour:02}:{endTimeMin:02}"
            formatted_reservations.append(
                {'time':time, 'end_time':endTime, 
                 'description': reservation[2],'user_reservation': reservation[3]}
            )

        # Tri par insertion
        for i in range(1, len(formatted_reservations)):
            key = formatted_reservations[i]
            j = i - 1

            # Insère key dans la bonne position
            while j >= 0 and key['time'] < formatted_reservations[j]['time']:
                j -= 1
            formatted_reservations.insert(j + 1, formatted_reservations.pop(i))

        return formatted_reservations

class db:
    # Supprime une reservation
    def delReservations(token, time):
        try:
            cursor.execute("DELETE FROM reservations WHERE user_token=? AND time=?", (token, time))
            conn.commit()
            
            if cursor.rowcount == 0 or 1: DbgPrint("[+] Réservation supprimée avec succès.", "green")
            else: DbgPrint("[-] Aucune réservation trouvée avec ces paramètres.", "red")

        except:
            DbgPrint("[-] DELETE failed", "red")  
            return
    
    # Vérifie que la public id de la carte est enregistrer dans la DB
    def checkTokenValid(token) -> bool:
        try:
            cursor.execute("SELECT card_uid FROM users WHERE token=?", (token,))
            if cursor.fetchone(): return True

            return False
        except:
            DbgPrint("[-] SELECT failed, check token valid", "red")  
            return None

    # Récupere l'heure et la durée des réservation du jour
    def fetchDateReservations(date):
        try:
            cursor.execute("SELECT time, duration, description, user_token FROM reservations WHERE date=?", (date,))
            result = cursor.fetchall()

            if result: return result 
            else: return []
        except:
            DbgPrint("[-] SELECT failed, reservations") 
            return []

    # Récupere le nom d'utilisateur depuis son token
    def fetchUsernameFromToken(token):
        try:
            cursor.execute("SELECT username FROM users WHERE token=?", (token,))
            v_tempUser = cursor.fetchone()
            return v_tempUser[0]
        except:
            DbgPrint("[-] SELECT failed, username from token", "red")
            return False
    
    # Récupere le mot de passe et le token depuis le nom d'utilisateur
    def fetchPasswordTokenFromUsername(username):
        try:
            v_tempUser = []
            cursor.execute("SELECT password, token FROM users WHERE username=?", (username,))
            v_tempUser.append(cursor.fetchone())
            user = {"password": v_tempUser[0][0], "token": v_tempUser[0][1]}
            return user
        except:
            DbgPrint("[-] SELECT failed, pass/token from username", "red")
            return False

    # Récupere le token depuis l'UID de la carte
    def fetchTokenFromCardUid(uid):
        try:
            cursor.execute("SELECT token FROM users WHERE card_uid=?", (uid,))
            token = cursor.fetchone()
            return token[0] if token else None
        except:
            DbgPrint("[-] SELECT failed, Token from UID", "red")
            return False
    
    def fetchReservationFromTokenDate(token,date):
        try:
            cursor.execute("SELECT time, duration FROM reservations WHERE user_token=? AND date=?", (token, date))
            reservations = cursor.fetchall()
            return reservations
        except:
            DbgPrint("[-] SELECT failed, Reservation from token", "red")
            return False

    # Enregistrement de la reservation dans la DB
    def sumbitReservationDB(date, time, duration, token, description) -> bool:
        try:
            cursor.execute("INSERT INTO reservations (user_token, date, time, duration, description) VALUES (?, ?, ?, ?, ?)",
                            (token, date, time, duration, description))
            conn.commit()
            return True
        except:
            DbgPrint("[-] INSERT failed", "red")  
            return False
    
    # Vérifie la connexion a la DB
    def testConnection() -> bool:
        try:
            cursor.execute("SELECT id FROM users WHERE id=1")
            if(cursor.fetchone()): return True
            else: return False
        except:
            DbgPrint("[-] test failed", "red")  
            return None

    # Création des tables de la DB
    def createTables() -> bool:
        try:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    card_uid TEXT UNIQUE,
                    token VARCHAR(128) UNIQUE NOT NULL,
                    mail VARCHAR(255) NOT NULL,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS reservations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_token VARCHAR(128) NOT NULL,
                    date DATE NOT NULL,
                    time TIME NOT NULL,
                    duration TIME NOT NULL,
                    description TEXT,
                    UNIQUE(date, time),
                    FOREIGN KEY(user_token) REFERENCES users(token)
                )
            ''')

            conn.commit()
            return True
        except: return False



###################################
        

class test:
    # Création d'un user de test
    def createTestUser() -> bool:
        try:
            password = "test"
            hashed_pass = bcrypt.hashpw(password.encode('utf-8'),bcrypt.gensalt())
            cursor.execute("INSERT INTO users (card_UID, token, mail, username, password) VALUES (?, ?, ?, ?, ?)", ("00:00:01", 1,"test@test.test","test", hashed_pass))
            conn.commit()
            return True
        except: return False
    
    # Création d'un utilisateur
    def createUser(username, password, mail, UID,token) -> bool:
        try:
            hashed_pass = bcrypt.hashpw(password.encode('utf-8'),bcrypt.gensalt())
            cursor.execute("INSERT INTO users (card_UID, token, mail, username, password) VALUES (?, ?, ?, ?, ?)", (UID, token,mail,username, hashed_pass))
            conn.commit()
            return True
        except: return False