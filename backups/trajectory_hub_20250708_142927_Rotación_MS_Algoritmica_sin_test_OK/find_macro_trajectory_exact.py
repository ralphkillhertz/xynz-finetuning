# === find_macro_trajectory_exact.py ===
# 🔍 Buscar MacroTrajectory con más precisión
# ⚡ Localizar exactamente dónde está y su estructura

import re

print("🔍 Buscando MacroTrajectory con precisión...\n")

file_path = "trajectory_hub/core/motion_components.py"

with open(file_path, 'r') as f:
    content = f.read()
    lines = content.split('\n')

# Buscar la línea exacta donde empieza MacroTrajectory
for i, line in enumerate(lines):
    if 'class MacroTrajectory' in line:
        print(f"✅ ENCONTRADO en línea {i+1}: {line}")
        
        # Mostrar contexto (20 líneas después)
        print("\n📝 Estructura de la clase:")
        for j in range(i, min(i+40, len(lines))):
            print(f"{j+1:4d}: {lines[j]}")
            
            # Si encontramos calculate_delta, notificar
            if 'calculate_delta' in lines[j]:
                print("\n⚠️ YA TIENE calculate_delta!")
                break
            
            # Si llegamos a otra clase, parar
            if j > i and lines[j].startswith('class '):
                break
        break

# También buscar cómo se usa en set_macro_trajectory
print("\n\n🔍 Buscando uso en set_macro_trajectory...")
engine_path = "trajectory_hub/core/enhanced_trajectory_engine.py"

with open(engine_path, 'r') as f:
    content = f.read()

# Extraer el método completo
match = re.search(r'def set_macro_trajectory\(.*?\):\s*\n(.*?)(?=\n    def|\Z)', content, re.DOTALL)
if match:
    method_body = match.group(0)
    print("\n📝 Método set_macro_trajectory:")
    
    # Buscar la línea donde crea MacroTrajectory
    lines = method_body.split('\n')
    for i, line in enumerate(lines[:30]):  # Primeras 30 líneas
        if 'MacroTrajectory' in line:
            print(f"  Línea clave: {line.strip()}")
            
            # Mostrar contexto
            start = max(0, i-2)
            end = min(len(lines), i+3)
            print("\n  Contexto:")
            for j in range(start, end):
                print(f"    {lines[j]}")

# Buscar si ya existe un método update en MacroTrajectory
print("\n\n🔍 Verificando si MacroTrajectory tiene método update...")
with open(file_path, 'r') as f:
    content = f.read()

# Buscar dentro de la clase MacroTrajectory
class_match = re.search(r'class MacroTrajectory.*?(?=\nclass|\Z)', content, re.DOTALL)
if class_match:
    class_content = class_match.group(0)
    
    # Buscar métodos
    methods = re.findall(r'def (\w+)\(', class_content)
    print(f"\n📋 Métodos en MacroTrajectory:")
    for method in methods:
        print(f"  - {method}")
        
    if 'calculate_delta' in methods:
        print("\n⚠️ ¡MacroTrajectory YA TIENE calculate_delta!")
        print("Necesitamos verificar si está implementado correctamente.")
    else:
        print("\n✅ MacroTrajectory NO tiene calculate_delta - procediendo con migración")

# Ver la estructura de datos que usa
print("\n\n🔍 Analizando estructura de datos...")
if 'trajectory_type' in class_content:
    print("✅ Usa trajectory_type")
if 'MacroTrajectoryType' in class_content:
    print("✅ Usa MacroTrajectoryType enum")
if 'movement_mode' in class_content:
    print("✅ Tiene movement_mode")