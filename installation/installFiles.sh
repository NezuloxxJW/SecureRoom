#!/bin/bash

# Définir le répertoire source
SOURCE_DIR="/home/administrator/SecureRoom"

# 1. Copier les fichiers HTML
echo "Copie des fichiers HTML vers /var/www/"
sudo cp -r "$SOURCE_DIR/html/" /var/www/

# 2. Copier la configuration Nginx
echo "Copie des fichiers de configuration Nginx vers /etc/nginx/sites-available/"
sudo cp -r "$SOURCE_DIR/nginx/sites-available/" /etc/nginx/

# 3. Copier les certificats
echo "Copie des certificats vers /etc/nginx/"
sudo cp "$SOURCE_DIR/cert/cert.pem" /etc/nginx/
sudo cp "$SOURCE_DIR/cert/key.pem" /etc/nginx/

# 4. Copier le service systemd
echo "Copie du fichier de service vers /etc/systemd/system/"
sudo cp "$SOURCE_DIR/service/server.service" /etc/systemd/system/
sudo systemctl enable server.service

sudo sh -c 'echo blacklist pn533_usb >> /etc/modprobe.d/blacklist-nfc.conf'

# Message de fin
echo "Déploiement terminé avec succès."
