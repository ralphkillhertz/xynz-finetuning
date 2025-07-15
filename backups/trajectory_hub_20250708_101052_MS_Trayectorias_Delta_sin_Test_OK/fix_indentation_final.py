# === fix_indentation_final.py ===
# 🔧 Fix: Solución definitiva para el error de indentación
# ⚡ Encuentra y corrige todos los problemas de indentación

import os
import shutil
from datetime import datetime

print("🔧 Arreglo FINAL de indentación...")

file_path = "trajectory_hub/core/motion_components.py"
backup_path = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy2(file_path, backup_path)

with open(file_path, 'r') as f:
    lines = f.readlines()

# Arreglar línea por línea con reglas claras
fixed_lines = []
in_class = False
in_method = False
class_indent = 0
method_indent = 0

for i, line in enumerate(lines):
    stripped = line.strip()
    
    # Detectar inicio de clase
    if stripped.startswith("class ") and not in_method:
        in_class = True
        in_method = False
        class_indent = len(line) - len(line.lstrip())
        fixed_lines.append(line)
        continue
    
    # Detectar inicio de método
    if in_class and stripped.startswith("def ") and not in_method:
        # Los métodos deben tener class_indent + 4
        correct_indent = class_indent + 4
        fixed_line = " " * correct_indent + stripped + "\n"
        fixed_lines.append(fixed_line)
        in_method = True
        method_indent = correct_indent
        continue
    
    # Líneas vacías - mantener vacías
    if not stripped:
        fixed_lines.append("\n")
        continue
    
    # Detectar fin de método (siguiente def o class)
    if in_method and (stripped.startswith("def ") or stripped.startswith("class ")):
        in_method = False
        # Retrasar el procesamiento de esta línea
        if stripped.startswith("def "):
            correct_indent = class_indent + 4
            fixed_line = " " * correct_indent + stripped + "\n"
            fixed_lines.append(fixed_line)
            in_method = True
            method_indent = correct_indent
        else:
            # Nueva clase
            in_class = True
            in_method = False
            class_indent = len(line) - len(line.lstrip())
            fixed_lines.append(line)
        continue
    
    # Líneas dentro de método
    if in_method:
        # Mantener indentación relativa
        current_indent = len(line) - len(line.lstrip())
        if current_indent > 0:  # No es línea vacía
            # Si tiene """ al principio, es docstring - usar method_indent + 4
            if stripped.startswith('"""'):
                fixed_line = " " * (method_indent + 4) + stripped + "\n"
            else:
                # Mantener indentación relativa al método
                relative_indent = current_indent - method_indent
                if relative_indent < 0:
                    relative_indent = 4  # Mínimo 4 espacios dentro del método
                fixed_line = " " * (method_indent + relative_indent) + stripped + "\n"
            fixed_lines.append(fixed_line)
        else:
            fixed_lines.append(line)
    else:
        # Fuera de clase/método
        fixed_lines.append(line)

# Guardar
with open(file_path, 'w') as f:
    f.writelines(fixed_lines)

print(f"✅ Backup: {backup_path}")

# Verificar que funciona
print("\n🧪 Verificando...")
try:
    # Forzar reimport
    import importlib
    import trajectory_hub
    importlib.reload(trajectory_hub)
    from trajectory_hub import EnhancedTrajectoryEngine
    print("✅ ¡Import exitoso!")
    
    # Ejecutar el test
    print("\n🏃 Ejecutando test...")
    import subprocess
    result = subprocess.run(['python', 'test_individual_fixed.py'], 
                          capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("Errores:", result.stderr)
        
except Exception as e:
    print(f"❌ Error: {e}")
    print("\n🔄 Intentando restaurar y arreglar de otra forma...")
    
    # Restaurar y hacer arreglo manual
    shutil.copy2(backup_path, file_path)
    
    # Leer todo el contenido
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Buscar y arreglar específicamente el problema en línea 721
    lines = content.split('\n')
    
    # Buscar la línea con set_rotation
    for i, line in enumerate(lines):
        if 'def set_rotation' in line and i > 700:  # Cerca de línea 721
            print(f"\n🎯 Encontrado en línea {i+1}: {line[:50]}...")
            # Asegurar 4 espacios de indentación
            lines[i] = '    def set_rotation(self, pitch: float = 0.0, yaw: float = 0.0, roll: float = 0.0, enabled: bool = True):'
            print("✅ Corregido a 4 espacios")
            break
    
    # Guardar
    with open(file_path, 'w') as f:
        f.write('\n'.join(lines))
    
    print("✅ Arreglo manual aplicado")

print("\n📝 Ejecuta: python test_individual_fixed.py")