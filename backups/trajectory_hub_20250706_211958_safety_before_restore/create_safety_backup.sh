#!/bin/bash
# BACKUP COMPLETO ANTES DE CAMBIOS
timestamp=$(date +%Y%m%d_%H%M%S)
backup_dir="trajectory_hub_backup_before_parallel_$timestamp"
echo "Creating complete backup: $backup_dir"
cp -r trajectory_hub "$backup_dir"
echo "✅ Backup complete: $backup_dir"
echo "To restore: rm -rf trajectory_hub && cp -r $backup_dir trajectory_hub"
