#!/bin/bash

# Configuration
DB_FILE="/home/administrator/Server/reservations.db"  # Chemin vers le fichier .db
BACKUP_DIR="/mnt/backup/db"      # Chemin vers le dossier de sauvegarde

# Vérifier si le fichier de base de données existe
if [ ! -f "$DB_FILE" ]; then
    echo "Erreur : Le fichier de base de données $DB_FILE n'existe pas."
    exit 1
fi

# Vérifier si le script a accès au fichier
if [ ! -r "$DB_FILE" ]; then
    echo "Erreur : Le script n'a pas accès en lecture au fichier $DB_FILE."
    exit 1
fi

# Créer le dossier de sauvegarde s'il n'existe pas
mkdir -p "$BACKUP_DIR"

# Date actuelle pour le nom de la sauvegarde
DATE=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/backup_${DATE}.db"

# Copier le fichier .db vers le dossier de sauvegarde
cp "$DB_FILE" "$BACKUP_FILE"

# Vérification de la réussite de la copie
if [ $? -eq 0 ]; then
    echo "Sauvegarde réussie : $BACKUP_FILE"

    # Supprimer les sauvegardes les plus anciennes si plus de 5 existent
   find "$BACKUP_DIR" -name "backup_*.db" -type f | sort -r | tail -n +6 | xargs -I {} rm -- {}
else
    echo "Erreur lors de la copie du fichier .db."
fi

