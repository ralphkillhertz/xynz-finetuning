# === find_correct_backup.py ===
# 🔍 Encontrar el backup correcto con las migraciones
# ⚡ O arreglar el import problemático

import os
import glob
from datetime import datetime

print("🔍 BUSCANDO BACKUPS DISPONIBLES...\n")

# Listar todos los backups
backups = glob.glob("trajectory_hub/core/enhanced_trajectory_engine.py.backup_*")
backups.sort()

print(f"📦 Total de backups encontrados: {len(backups)}\n")

# Mostrar los últimos 10
print("Últimos 10 backups:")
for backup in backups[-10:]:
    # Extraer fecha del nombre
    filename = os.path.basename(backup)
    print(f"  - {filename}")

# El más reciente antes del problema
print(f"\n📌 Backup más reciente: {backups[-1] if backups else 'Ninguno'}")

# Arreglar el import problemático
print("\n🔧 ARREGLANDO IMPORT PROBLEMÁTICO...")

engine_path = "trajectory_hub/core/enhanced_trajectory_engine.py"

with open(engine_path, 'r') as f:
    content = f.read()

# Eliminar import problemático
if "from .motion_components import create_complex_movement" in content:
    content = content.replace(
        "from .motion_components import create_complex_movement",
        "# from .motion_components import create_complex_movement  # Eliminado - no existe"
    )
    print("✅ Import problemático comentado")

# Buscar otros imports problemáticos
imports_to_check = [
    "create_complex_movement",
    "TrajectoryType",
    "MotionState"
]

for imp in imports_to_check:
    if f"from .motion_components import {imp}" in content:
        print(f"⚠️ Encontrado import de {imp}")

# Guardar
with open(engine_path, 'w') as f:
    f.write(content)

# Ahora aplicar las migraciones necesarias
print("\n🔧 APLICANDO MIGRACIONES NECESARIAS...")

# 1. Asegurar que _macros esté inicializado
if "self._macros = {}" not in content:
    print("❌ Falta self._macros = {}")
    # Buscar __init__ y añadirlo
    import re
    init_match = re.search(r'def __init__\(.*?\):.*?(?=\n    def)', content, re.DOTALL)
    if init_match:
        init_content = init_match.group(0)
        if "self.motion_states = {}" in init_content and "self._macros = {}" not in init_content:
            new_init = init_content.replace(
                "self.motion_states = {}",
                "self._macros = {}  # Almacén de macros\n        self.motion_states = {}"
            )
            content = content.replace(init_content, new_init)
            print("✅ Añadido self._macros = {}")

# 2. Verificar que MacroTrajectory tenga calculate_delta
mc_path = "trajectory_hub/core/motion_components.py"
with open(mc_path, 'r') as f:
    mc_content = f.read()

if "class MacroTrajectory" in mc_content and "def calculate_delta" not in mc_content[mc_content.find("class MacroTrajectory"):]:
    print("❌ MacroTrajectory no tiene calculate_delta")
    print("   Necesita ser migrado")
else:
    print("✅ MacroTrajectory tiene calculate_delta")

# Guardar cambios
with open(engine_path, 'w') as f:
    f.write(content)

# Test
print("\n🧪 Test rápido...")
try:
    from trajectory_hub import EnhancedTrajectoryEngine
    print("✅ Import exitoso!")
    
    # Verificar que el sistema funcione
    engine = EnhancedTrajectoryEngine(max_sources=5, fps=60)
    print("✅ Engine creado")
    
    # Ejecutar test completo si todo está bien
    import subprocess
    print("\n🧪 Ejecutando test completo...")
    result = subprocess.run(['python', 'test_macro_system_fixed.py'], 
                          capture_output=True, text=True)
    
    if result.returncode == 0:
        for line in result.stdout.split('\n'):
            if any(word in line for word in ['✅', '❌', 'ÉXITO', 'Macro']):
                print(line)
    else:
        print(f"❌ Error: {result.stderr}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    
print("\n💡 RECOMENDACIÓN:")
print("Si los backups están corruptos, podemos:")
print("1. Usar el backup del 8 de julio más reciente")
print("2. O reconstruir create_macro desde cero")
print("3. O continuar con servidor MCP y volver a esto después")