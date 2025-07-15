# === find_macro_rotation_error.py ===
# 🎯 Buscar el error específico en MacroRotation
# ⚡ Análisis profundo del flujo de procesamiento

import os
import traceback

print("🔍 Buscando el error en MacroRotation\n")

# Archivo de componentes
filepath = './trajectory_hub/core/motion_components.py'

if not os.path.exists(filepath):
    print(f"❌ No se encuentra {filepath}")
    exit(1)

with open(filepath, 'r') as f:
    lines = f.readlines()

print("1️⃣ Analizando clase MacroRotation completa:\n")

# Encontrar la clase MacroRotation
in_class = False
class_start = 0
class_lines = []

for i, line in enumerate(lines):
    if 'class MacroRotation' in line:
        in_class = True
        class_start = i
        print(f"✅ Clase encontrada en línea {i+1}")
        
    if in_class:
        # Si encontramos otra clase, terminamos
        if line.strip().startswith('class ') and i > class_start:
            break
            
        class_lines.append((i, line))

# Buscar comparaciones problemáticas en MacroRotation
print("\n2️⃣ Buscando comparaciones con arrays en MacroRotation:\n")

for i, line in class_lines:
    # Buscar if statements que puedan tener problemas
    if 'if ' in line and not line.strip().startswith('#'):
        # Excluir casos seguros
        if 'isinstance' in line or 'getattr' in line or 'is None' in line:
            continue
            
        # Buscar comparaciones sospechosas
        if any(word in line for word in ['enabled', 'speed', 'phase', 'center']):
            print(f"   Línea {i+1}: {line.strip()}")
            
            # Verificar si es una comparación directa
            if ' and ' not in line and ' or ' not in line:
                if '==' in line or '!=' in line or ' if ' in line:
                    print(f"      ⚠️ POSIBLE PROBLEMA - comparación directa")

print("\n3️⃣ Analizando método calculate_delta de MacroRotation:\n")

# Buscar calculate_delta específicamente
in_calculate_delta = False
method_indent = 0

for i, line in class_lines:
    if 'def calculate_delta' in line:
        in_calculate_delta = True
        method_indent = len(line) - len(line.lstrip())
        print(f"✅ calculate_delta encontrado en línea {i+1}")
        print("\n   Contenido del método:")
        
    if in_calculate_delta:
        current_indent = len(line) - len(line.lstrip())
        
        # Si volvemos al nivel de indentación del método, terminamos
        if line.strip() and current_indent <= method_indent and 'def calculate_delta' not in line:
            in_calculate_delta = False
            continue
            
        # Mostrar el contenido
        print(f"   {i+1}: {line.rstrip()}")
        
        # Buscar comparaciones problemáticas
        if 'if ' in line and 'self.' in line:
            print(f"      >>> VERIFICAR ESTA LÍNEA")

print("\n4️⃣ Buscando en update_with_deltas donde se procesa macro_rotation:\n")

# Buscar update_with_deltas
in_update = False
found_macro_rotation = False

for i, line in enumerate(lines):
    if 'def update_with_deltas' in line:
        in_update = True
        continue
        
    if in_update:
        if line.strip() and not line.strip().startswith('#') and line[0] not in ' \t':
            in_update = False
            
        if 'macro_rotation' in line:
            found_macro_rotation = True
            # Mostrar contexto
            start = max(0, i-5)
            end = min(len(lines), i+10)
            print(f"\n   Contexto alrededor de línea {i+1}:")
            for j in range(start, end):
                marker = ">>>" if j == i else "   "
                print(f"   {marker} {j+1}: {lines[j].rstrip()}")

# Test rápido de numpy
print("\n5️⃣ Test rápido de comparaciones numpy:\n")

test_code = """
import numpy as np

# Simular lo que podría estar pasando
speed_array = np.array([0.0, 1.0, 0.0])
enabled = True

print("Test 1 - Comparación directa de array:")
try:
    if speed_array:  # Esto causa el error
        print("  No debería llegar aquí")
except ValueError as e:
    print(f"  ❌ Error: {e}")

print("\\nTest 2 - Comparación correcta:")
if np.any(speed_array):  # Esto es correcto
    print("  ✅ Array tiene valores no-cero")

print("\\nTest 3 - enabled como array:")
enabled_array = np.array([True])
try:
    if enabled_array:  # Esto también causa error si es array
        print("  No debería llegar aquí")
except ValueError as e:
    print(f"  ❌ Error: {e}")
"""

print("Ejecutando tests de numpy:")
exec(test_code)

print("\n" + "="*50)
print("\n💡 CONCLUSIÓN: Buscar dónde self.enabled, speed o phase se comparan directamente")
print("   sin usar getattr(), isinstance() o conversiones explícitas")