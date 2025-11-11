#!/bin/bash
# backup.sh - Simple backup script for personal TTRPG data

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="backups"
BACKUP_FILE="${BACKUP_DIR}/ttrpg_backup_${DATE}.tar.gz"

# Create backup directory if it doesn't exist
mkdir -p "${BACKUP_DIR}"

echo "📦 Creating backup of TTRPG data..."

# Backup important data directories
tar -czf "${BACKUP_FILE}" \
    character_info/ \
    chat_histories/ \
    embeddings/ \
    static/dune/system_prompt.txt \
    static/the-one-ring/system_prompt.txt \
    static/zweihander/system_prompt.txt \
    system_prompt.txt \
    2>/dev/null || echo "⚠️  Some files may not exist yet - this is normal for new installations"

if [ -f "${BACKUP_FILE}" ]; then
    BACKUP_SIZE=$(du -h "${BACKUP_FILE}" | cut -f1)
    echo "✅ Backup created: ${BACKUP_FILE} (${BACKUP_SIZE})"
    
    # Keep only last 10 backups
    ls -t "${BACKUP_DIR}"/ttrpg_backup_*.tar.gz 2>/dev/null | tail -n +11 | xargs rm -f 2>/dev/null
    echo "🧹 Cleaned up old backups (keeping last 10)"
else
    echo "❌ Backup failed"
    exit 1
fi
