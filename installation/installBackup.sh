#!/bin/bash

# Variables
DISQUE="/dev/sdb1"  # Remplace par le bon identifiant de ton deuxième disque
MONTAGE="/mnt/backup"
BACKUP_SCRIPT="/home/administrator/SecureRoom/backup/backup.sh"  # Chemin de ton script de sauvegarde
LOG_FILE="$MONTAGE/log.txt"  # Chemin du fichier log

# 1. Vérifier si le disque est monté et le démonter si nécessaire
if mount | grep "$DISQUE" > /dev/null; then
    echo "Le disque $DISQUE est monté. Démontage en cours..."
    sudo umount $DISQUE
    if [ $? -ne 0 ]; then
        echo "Erreur lors du démontage du disque $DISQUE. Veuillez vérifier."
        exit 1
    fi
else
    echo "Le disque $DISQUE n'est pas monté."
fi

# 2. Formater le disque en ext4
echo "Formattage du disque $DISQUE en ext4..."
sudo mkfs.ext4 $DISQUE

# 3. Créer le point de montage si nécessaire
if [ ! -d "$MONTAGE" ]; then
    echo "Création du répertoire de montage $MONTAGE..."
    sudo mkdir -p $MONTAGE
fi

# 4. Monter le disque
echo "Montage du disque $DISQUE sur $MONTAGE..."
sudo mount $DISQUE $MONTAGE

# 5. Créer les dossiers bd et misc, et le fichier log.txt
echo "Création des répertoires bd et misc et du fichier log.txt..."
sudo mkdir -p "$MONTAGE/bd" "$MONTAGE/misc"
sudo touch "$LOG_FILE"

# 6. Ajouter le montage au fstab pour qu'il soit monté au démarrage
echo "$DISQUE $MONTAGE ext4 defaults 0 2" | sudo tee -a /etc/fstab

# 7. Ajouter le script de sauvegarde au crontab
CRON_JOB="0 0 * * * $BACKUP_SCRIPT"  # Exécute le script tous les jours à minuit
( crontab -l; echo "$CRON_JOB" ) | crontab -

echo "Configuration terminée. Le script de sauvegarde sera exécuté selon le cron."
