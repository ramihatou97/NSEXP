#!/bin/sh
# NSSP Database Backup Script

set -e

# Configuration
BACKUP_DIR="/backups"
DB_HOST="postgres-primary"
DB_PORT="5432"
DB_NAME="${POSTGRES_DB:-neurosurgical_knowledge}"
DB_USER="${POSTGRES_USER:-neurosurg}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/nssp_backup_$TIMESTAMP.sql"
BACKUP_ARCHIVE="$BACKUP_DIR/nssp_backup_$TIMESTAMP.tar.gz"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

echo "Starting backup of $DB_NAME at $(date)"

# Perform database dump
PGPASSWORD="$POSTGRES_PASSWORD" pg_dump \
    -h "$DB_HOST" \
    -p "$DB_PORT" \
    -U "$DB_USER" \
    -d "$DB_NAME" \
    --verbose \
    --no-owner \
    --no-acl \
    --format=plain \
    > "$BACKUP_FILE"

# Compress the backup
tar -czf "$BACKUP_ARCHIVE" -C "$BACKUP_DIR" "$(basename $BACKUP_FILE)"
rm "$BACKUP_FILE"

echo "Backup completed: $BACKUP_ARCHIVE"

# Keep only last 7 days of backups
find "$BACKUP_DIR" -name "nssp_backup_*.tar.gz" -mtime +7 -delete

echo "Cleanup completed. Backup process finished at $(date)"