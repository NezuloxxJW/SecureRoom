sudo echo "allow_anonymous false" >> /etc/mosquitto/conf.d/default.conf
sudo echo "password_file /etc/mosquitto/passwd" >> /etc/mosquitto/conf.d/default.conf
sudo echo "listener 1883" >> /etc/mosquitto/conf.d/default.conf

sudo touch /etc/mosquitto/passwd
sudo echo "admin_eptm:12345-" >> /etc/mosquitto/passwd
sudo mosquitto_passwd -U /etc/mosquitto/passwd

sudo systemctl restart mosquitto