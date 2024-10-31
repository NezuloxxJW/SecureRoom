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
sudo cp -r "$SOURCE_DIR/cert/*" /etc/nginx/

# 4. Copier le service systemd
echo "Copie du fichier de service vers /etc/systemd/system/"
sudo cp "$SOURCE_DIR/service/server.service" /etc/systemd/system/

# Message de fin
echo "Déploiement terminé avec succès."
