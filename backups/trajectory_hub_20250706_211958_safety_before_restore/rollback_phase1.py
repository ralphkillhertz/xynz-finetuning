#!/usr/bin/env python3
"""
⏮️ ROLLBACK FASE 1
"""

import os
import shutil

print("⏮️ Revirtiendo cambios de Fase 1...")

# Restaurar desde backups
backup_dir = "phase1_backups_20250705_131505"

for file in os.listdir(backup_dir):
    if file.endswith('.py'):
        src = os.path.join(backup_dir, file)
        # Encontrar destino original
        for root, dirs, files in os.walk("trajectory_hub"):
            if file in files:
                dst = os.path.join(root, file)
                print(f"Restaurando: {dst}")
                shutil.copy2(src, dst)
                break

# Eliminar archivos creados
files_to_remove = [
    "trajectory_hub/core/compatibility.py",
    "trajectory_hub/config/parallel_config.json"
]

for file in files_to_remove:
    if os.path.exists(file):
        os.remove(file)
        print(f"Eliminado: {file}")

print("✅ Rollback de Fase 1 completado")
