# === migrate_to_new_controller.py ===
# 🔄 Script para migrar al nuevo controlador
# ⚡ Reemplaza el controlador antiguo con el nuevo

import os
import shutil
from datetime import datetime

print("🔄 MIGRANDO AL NUEVO CONTROLADOR")
print("=" * 60)

# Archivos
old_controller = "trajectory_hub/interface/interactive_controller.py"
new_controller = "trajectory_hub/interface/interactive_controller_v2.py"
backup_name = f"interactive_controller_old_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"

# 1. Hacer backup del antiguo
if os.path.exists(old_controller):
    backup_path = os.path.join(os.path.dirname(old_controller), backup_name)
    shutil.copy2(old_controller, backup_path)
    print(f"✅ Backup creado: {backup_path}")

# 2. Reemplazar con el nuevo
shutil.copy2(new_controller, old_controller)
print(f"✅ Controlador actualizado: {old_controller}")

# 3. Eliminar archivo temporal
os.remove(new_controller)
print(f"✅ Archivo temporal eliminado")

print("\n✅ MIGRACIÓN COMPLETA")
print("\n🚀 Prueba el nuevo controlador con:")
print("   python -m trajectory_hub.interface.interactive_controller")
