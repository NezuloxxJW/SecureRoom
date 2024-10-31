#!/bin/bash

# Variables
DISQUE="/dev/sdb"  # Remplace par le bon identifiant de ton deuxième disque
MONTAGE="/mnt/backup"
BACKUP_SCRIPT="/home/administrator/SecureRoom/backup/backup.sh"  # Chemin de ton script de sauvegarde

# 1. Formater le disque en ext4
echo "Formattage du disque $DISQUE en ext4..."
sudo mkfs.ext4 $DISQUE

# 2. Créer le point de montage si nécessaire
if [ ! -d "$MONTAGE" ]; then
    echo "Création du répertoire de montage $MONTAGE..."
    sudo mkdir -p $MONTAGE
fi

# 3. Monter le disque
echo "Montage du disque $DISQUE sur $MONTAGE..."
sudo mount $DISQUE $MONTAGE

# 4. Ajouter le montage au fstab pour qu'il soit monté au démarrage
echo "$DISQUE $MONTAGE ext4 defaults 0 2" | sudo tee -a /etc/fstab

# 5. Ajouter le script de sauvegarde au crontab
CRON_JOB="0 0 * * * $BACKUP_SCRIPT"  # Exécute le script tous les jours à 2h du matin
( crontab -l; echo "$CRON_JOB" ) | crontab -

echo "Configuration terminée. Le script de sauvegarde sera exécuté selon le cron."
