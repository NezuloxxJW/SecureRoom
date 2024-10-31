import paho.mqtt.client as mqtt

# Liste pour stocker les topics rencontrés
topics_recus = set()

# Variable pour stocker l'ID
nuki_id = None

# Fonction de rappel lorsque le client se connecte au broker
def on_connect(client, userdata, flags, rc):
    print("Connecté avec le code de résultat: " + str(rc))
    # S'abonner à tous les topics nuki
    client.subscribe("nuki/#")

# Fonction de rappel lorsque le client reçoit un message
def on_message(client, userdata, msg):
    global nuki_id
    
    nuki_id = msg.topic.split("/")[1]  # Récupère l'ID
    print(f"ID reçu: {nuki_id}")

    client.unsubscribe("nuki/#")
    print("Désabonné des topics nuki.")
    # Optionnel: publie sur le topic nuki/<ID>/lockAction
    action_topic = f"nuki/{nuki_id}/lockAction"
    client.publish(action_topic, "2")  # Envoie 1 à lockAction
    print(f"Message envoyé à {action_topic} avec la valeur 1")

# Créer un client MQTT
client = mqtt.Client()

# Définir les fonctions de rappel
client.on_connect = on_connect
client.on_message = on_message

username = "admin_eptm"
password = "12345-"
client.username_pw_set(username, password)

# Se connecter au broker MQTT (remplacez l'URL et le port par ceux de votre broker)
client.connect("127.0.0.1", 1883, 60)

# Lancer le loop pour gérer les callbacks
client.loop_start()

# Garder le programme en cours d'exécution
try:
    while True:
        pass
except KeyboardInterrupt:
    print("Déconnexion...")
    client.loop_stop()
    client.disconnect()
