from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from flask_limiter import Limiter
from waitress import serve
import uuid
import threading
import nfc
import sys
import os
import time
import signal

from db import db, bcrypt, format, verify
from debug import DbgPrint
from _nfc import nfcReader, launchThreadNfc, signal_handler


#
# Globals
#

# Application flask + paramètres
app = Flask(__name__) 
app.secret_key = uuid.uuid4().hex
app.config.update(
    # éviter la récuperation des cookies depuis JS
    SESSION_COOKIE_HTTPONLY=True,
    # HTTPS only
    SESSION_COOKIE_SECURE=True
)
# Limiteur de requêtes à 10 par minute par adresse IP
limiter = Limiter(app)
# Cross-Origin Resource Sharing
CORS(app, supports_credentials=True)

#
# Fonctions applicatif
#


# Fonction pour supprimer une reservation
# @params : token:UUID, date:DATETIME, time:DATETIME 
# @return : status -> success/error
#
@app.route('/delete', methods=['POST'])
def delete():
    DbgPrint("[*] Delete requested", "yellow")
    token = request.cookies.get('auth_token')
    if not token:
        DbgPrint("[-] No Token", "red") 
        return jsonify({'status': 'error'}), 400
    
    DbgPrint("[+] Token", "green")
    
    data = request.get_json()
    date = data['date']
    time = data['time']
    
    reservations = db.fetchDateReservations(date)
    formatted_reservations = format.formatReservations(reservations)

    for reservation in formatted_reservations:
        if reservation['user_reservation'] == token:
            if reservation['time'] == time:
                db.delReservations(token,time)
                return jsonify({'status': 'success'}), 200
    
    DbgPrint("[-] Reservation not found / invalid request", "red")
    return jsonify({'status': 'error'}), 400

# Fonction pour se logout de son compte
# @params : aucun
# @return : vide le cookie du token
#
@app.route('/logout', methods=['POST'])
def logout():
    DbgPrint("[*] Logout asked")
    response = make_response(jsonify({'status': 'success','message': 'Logged out successfully'}), 200)
    response.set_cookie('auth_token', '', httponly=True, path='/', samesite="Lax", expires=0)
    
    DbgPrint("[+] Logout exited")
    return response

# Fonction pour se login
# @params : token:UUID, username:STR, password:STR
# @return : token -> UUID
#
# Si un token est déja existant il va se connecter a se compte automatiquement
#
@app.route('/login', methods=['POST'])
@limiter.limit("3 per minute")
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    token = request.cookies.get('auth_token')
    
    DbgPrint("[*] Login requested for " + username, "yellow")
    
    if(db.checkTokenValid(token)): 
        user = db.fetchUsernameFromToken(token)
        DbgPrint(f"[+] AutoLogin for {user}", "green")
        return jsonify({'status': 'success', 'username': user})

    if not username or not password:
        DbgPrint("[-] Missing user infos", "red")
        return jsonify({'error': 'Missing username or password'}), 400

    user = db.fetchPasswordTokenFromUsername(username)

    if user:
        hashed_password = user['password'] 
        if bcrypt.checkpw(password.encode('utf-8'), hashed_password): 
            response = make_response(jsonify({'status': 'success', 'username': username ,'message': 'Logged in successfully'}), 200)
            response.set_cookie('auth_token', user['token'], httponly=True, path='/', samesite="Lax")
            DbgPrint("[+] Login exited succesfully", "green")
            return response
        else:
            DbgPrint("[-] Wrong password", "red")
            return jsonify({'error': 'Invalid credentials'}), 401
    else:
        DbgPrint("[-] No user", "red")
        return jsonify({'error': 'Invalid credentials'}), 401

# Fonction pour ajouter une nouvelle reservation
# @params : token:UUID, date:DATETIME, time:DATETIME, duration:DATETIME, description:STR
# @return : status -> success/error
#
@app.route('/submit', methods=['POST'])
@limiter.limit("5 per minute") # Limite à 5 requêtes par minute
def submit():
    # Récupération des données
    data = request.get_json()
    date = data['date']
    time = data['time']
    duration = data['duration']
    description = data['description']
    
    token = request.cookies.get('auth_token')

    DbgPrint("[*] Submit requested", "yellow")

    DbgPrint("[~] Date : " + date)
    DbgPrint("[~] Time : " + time)
    DbgPrint("[~] Durée : " + duration)
    DbgPrint("[~] Desc : " + description)
    DbgPrint("[~] User token : " + token)

    reservations = db.fetchDateReservations(date)
    formatted_reservations = format.formatReservations(reservations)

    # Vérifier les données, enregistrer la reservation
    if not (verify.verifySumbitDatas(date,time,duration,token,description)):
        DbgPrint("[-] Data not valid","red")
        return jsonify({'status': 'error', 'message': 'Datas not valid'}), 400
    
    if not (verify.verifyOverlap(time,duration,formatted_reservations)):
        DbgPrint("[-] Overlap", "red")
        return jsonify({'status': 'error', 'message': 'Overlap'}), 400
    
    if(db.sumbitReservationDB(date,time,duration,token,description)):
        DbgPrint("[+] Submit exited succesfully", "green")
        return jsonify({'status': 'success', 'message': 'submitted'})

    DbgPrint("[-] Unknown error","red")
    return jsonify({'status': 'error', 'message': 'unknown error'}), 400

# Fonction qui recupère les reservations
# @params : date:DATETIME
# @return : time, endTime, description, isUserReservation
#
@app.route('/get_reservations', methods=['POST'])
def Fetch():
    # Récupération des données de la requete web
    data = request.get_json()
    date = data['date']

    token = request.cookies.get('auth_token')
    
    DbgPrint("[*] Fetch requested for : " + date, "yellow")
    
    # Récuperation des heures réservée
    reservations = db.fetchDateReservations(date)
    formatted_reservations = format.formatReservations(reservations)

    # Vérifie si c'est le même token que l'utilisateur qui a demandé
    for reservation in formatted_reservations:
        reservation['user_reservation'] = reservation['user_reservation'] == token
    
    DbgPrint("[+] Fetch exited succesfully", "green")
    return jsonify({'reserved': formatted_reservations, 'status' : 'success'}),200 


#
# Main
#
    
if __name__ == '__main__':
    if not (db.testConnection()):
        DbgPrint("[!!] DB not existing, creating DB and creating Tables")
        db.createTables()

    signal.signal(signal.SIGINT, signal_handler)

    launchThreadNfc()
    DbgPrint("[+] App is running, NFC thread is running", "magenta")
    serve(app, host="127.0.0.1", port=5000)

