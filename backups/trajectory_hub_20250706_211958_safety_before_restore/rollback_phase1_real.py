#!/usr/bin/env python3
"""⏮️ ROLLBACK FASE 1"""
import os
import shutil

backup_dir = "phase1_real_backups_20250705_161631"
print(f"Restaurando desde: {backup_dir}")

# Restaurar motion_components.py
if os.path.exists(f"{backup_dir}/motion_components.py"):
    shutil.copy2(f"{backup_dir}/motion_components.py", "trajectory_hub/core/motion_components.py")
    print("✅ motion_components.py restaurado")

# Eliminar archivos nuevos
for file in ["trajectory_hub/core/compatibility_v2.py", "trajectory_hub/config/parallel_config.json"]:
    if os.path.exists(file):
        os.remove(file)
        print(f"✅ {file} eliminado")

print("✅ Rollback completado")
