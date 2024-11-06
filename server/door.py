import paho.mqtt.client as mqtt
from debug import DbgPrint

nuki_ids = ['3AD7396C']

client = None

class door:
    def init():
        global client
        client = mqtt.Client()
        username = "admin_eptm"
        password = "12345-"
        client.username_pw_set(username, password)
        client.connect("192.168.0.10", 1883, 60)

    def open():
        door.init()
        action_topic = f"nuki/{nuki_ids[0]}/lockAction"
        client.publish(action_topic, "1")
        client.disconnect()
        DbgPrint("[+] Ouverture envoyée","green")
