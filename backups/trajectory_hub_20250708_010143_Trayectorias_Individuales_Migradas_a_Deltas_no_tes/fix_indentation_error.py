# === fix_indentation_error.py ===
# 🔧 Fix: Corregir error de indentación en línea 721
# ⚡ Arreglo rápido del problema

import os
import shutil
from datetime import datetime

print("🔧 Corrigiendo error de indentación...")

file_path = "trajectory_hub/core/motion_components.py"
backup_path = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy2(file_path, backup_path)

with open(file_path, 'r') as f:
    lines = f.readlines()

# Encontrar la línea problemática (línea 721 - ajustar por índice 0)
line_num = 720  # 721 - 1 para índice

print(f"Línea problemática: {lines[line_num].rstrip()}")

# Verificar indentación de líneas cercanas
print("\nContexto (líneas 715-725):")
for i in range(max(0, line_num-5), min(len(lines), line_num+5)):
    # Contar espacios al inicio
    spaces = len(lines[i]) - len(lines[i].lstrip())
    print(f"  {i+1} ({spaces} espacios): {lines[i].rstrip()[:60]}...")

# Arreglar la indentación de la línea problemática
# Buscar la indentación correcta mirando las líneas anteriores de métodos
for i in range(line_num-1, max(0, line_num-20), -1):
    if lines[i].strip().startswith("def ") and not lines[i].strip().startswith("def calculate_delta"):
        correct_indent = len(lines[i]) - len(lines[i].lstrip())
        print(f"\nIndentación correcta encontrada: {correct_indent} espacios (línea {i+1})")
        
        # Aplicar la indentación correcta
        lines[line_num] = " " * correct_indent + lines[line_num].lstrip()
        break

# Guardar el archivo corregido
with open(file_path, 'w') as f:
    f.writelines(lines)

print(f"✅ Backup: {backup_path}")
print("✅ Indentación corregida")

# Verificar que se puede importar
print("\n🧪 Verificando import...")
try:
    from trajectory_hub import EnhancedTrajectoryEngine
    print("✅ Import exitoso!")
except Exception as e:
    print(f"❌ Error: {e}")
    
    # Si sigue fallando, restaurar backup
    print("\n🔄 Restaurando backup...")
    shutil.copy2(backup_path, file_path)
    
    # Intentar arreglo más agresivo
    print("🔧 Aplicando arreglo más agresivo...")
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Buscar el método problemático y asegurar indentación consistente
    lines = content.split('\n')
    fixed_lines = []
    inside_class = False
    class_indent = 0
    
    for i, line in enumerate(lines):
        if line.strip().startswith("class ") and "IndividualTrajectory" in line:
            inside_class = True
            class_indent = len(line) - len(line.lstrip())
            fixed_lines.append(line)
        elif inside_class and line.strip().startswith("def "):
            # Asegurar que todos los métodos tengan indentación correcta
            method_line = " " * (class_indent + 4) + line.strip()
            fixed_lines.append(method_line)
        elif inside_class and line.strip().startswith("class "):
            # Nueva clase, salir
            inside_class = False
            fixed_lines.append(line)
        else:
            fixed_lines.append(line)
    
    # Guardar versión arreglada
    with open(file_path, 'w') as f:
        f.write('\n'.join(fixed_lines))
    
    print("✅ Arreglo agresivo aplicado")

print("\n📝 Ahora ejecuta: python test_individual_fixed.py")