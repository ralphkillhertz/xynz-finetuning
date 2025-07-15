# === fix_duplicate_methods.py ===
# 🔧 Fix: Eliminar update_with_deltas duplicado y arreglar estructura
# ⚡ Limpieza completa del desastre

import os
import shutil
from datetime import datetime

print("🔧 Arreglando estructura de SourceMotion...")

file_path = "trajectory_hub/core/motion_components.py"
backup_path = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy2(file_path, backup_path)

with open(file_path, 'r') as f:
    lines = f.readlines()

print(f"📄 Total líneas: {len(lines)}")

# Eliminar el update_with_deltas mal ubicado (líneas 108-121)
print("\n🗑️ Eliminando update_with_deltas mal ubicado...")

# Marcar líneas a eliminar
lines_to_remove = []
for i in range(107, min(122, len(lines))):  # Líneas 108-121
    if i < len(lines):
        print(f"  Eliminando L{i+1}: {lines[i].strip()[:50]}")
        lines_to_remove.append(i)

# Eliminar de atrás hacia adelante para no afectar índices
for i in reversed(lines_to_remove):
    del lines[i]

print(f"\n✅ Eliminadas {len(lines_to_remove)} líneas")

# Ahora actualizar el update_with_deltas bueno para que use dict
print("\n🔧 Actualizando update_with_deltas correcto...")

# Buscar el update_with_deltas restante
for i, line in enumerate(lines):
    if line.strip().startswith("def update_with_deltas") and len(line) - len(line.lstrip()) == 4:
        print(f"  Encontrado en línea {i+1}")
        
        # Reemplazar el método completo
        # Buscar el final del método
        method_end = i + 1
        while method_end < len(lines) and (lines[method_end].startswith("        ") or lines[method_end].strip() == ""):
            method_end += 1
        
        # Nuevo método corregido
        new_method = [
            "    def update_with_deltas(self, current_time: float, dt: float) -> list:\n",
            "        \"\"\"Actualiza componentes y retorna LISTA de deltas\"\"\"\n",
            "        deltas = []\n",
            "        \n",
            "        # active_components es un DICT\n",
            "        if isinstance(self.active_components, dict):\n",
            "            for name, component in self.active_components.items():\n",
            "                if component and hasattr(component, 'enabled') and component.enabled:\n",
            "                    if hasattr(component, 'calculate_delta'):\n",
            "                        delta = component.calculate_delta(self.state, dt)\n",
            "                        if delta and delta.position is not None:\n",
            "                            deltas.append(delta)\n",
            "        \n",
            "        return deltas\n",
            "\n"
        ]
        
        # Reemplazar
        lines[i:method_end] = new_method
        print("  ✅ Método actualizado")
        break

# Guardar
with open(file_path, 'w') as f:
    f.writelines(lines)

print(f"\n✅ Archivo corregido")
print(f"📁 Backup: {backup_path}")

# Verificar
print("\n🧪 Verificando...")
try:
    from trajectory_hub import EnhancedTrajectoryEngine
    print("✅ Import exitoso!")
    
    # Ejecutar test
    print("\n🚀 Ejecutando test final...")
    import subprocess
    result = subprocess.run(['python', 'test_individual_trajectory_final.py'], 
                          capture_output=True, text=True)
    
    if result.stdout:
        # Mostrar resultados importantes
        lines = result.stdout.strip().split('\n')
        for line in lines:
            if any(word in line for word in ['FINAL', 'RESULTADOS', '✅', '❌', 'MIGRACIÓN']):
                print(f"  {line}")
    
    if result.returncode != 0 and result.stderr:
        print(f"\n❌ Error: {result.stderr}")
        
except Exception as e:
    print(f"❌ Error: {e}")