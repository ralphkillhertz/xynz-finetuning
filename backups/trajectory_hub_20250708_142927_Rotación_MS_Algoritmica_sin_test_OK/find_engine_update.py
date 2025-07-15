# === find_engine_update.py ===
# 🔧 Fix: Encontrar cómo se llama realmente el método update
# ⚡ Puede tener parámetros o nombre diferente

import os
import re

print("🔍 Buscando el método update en EnhancedTrajectoryEngine...")

file_path = "trajectory_hub/core/enhanced_trajectory_engine.py"

with open(file_path, 'r') as f:
    content = f.read()

# Buscar todas las definiciones de métodos que contengan "update"
print("\n📋 Métodos con 'update' en el nombre:")
pattern = r'def .*update.*\([^)]*\):'
matches = list(re.finditer(pattern, content))

for match in matches:
    line_start = content.rfind('\n', 0, match.start()) + 1
    line_end = content.find('\n', match.end())
    line = content[line_start:line_end]
    line_num = content[:match.start()].count('\n') + 1
    print(f"  L{line_num}: {line.strip()}")

# Buscar métodos principales del engine
print("\n📋 Métodos principales del engine:")
pattern = r'def ([a-zA-Z_]+)\([^)]*\):'
matches = list(re.finditer(pattern, content))

# Mostrar los primeros 20 métodos
for i, match in enumerate(matches[:20]):
    method_name = match.group(1)
    if method_name not in ['__init__', '__str__', '__repr__']:
        line_num = content[:match.start()].count('\n') + 1
        print(f"  L{line_num}: def {method_name}(...)")

# Buscar específicamente métodos que podrían ser el loop principal
print("\n🔍 Buscando métodos que podrían ser el loop principal:")
for keyword in ['step', 'tick', 'process', 'run', 'loop']:
    pattern = f'def {keyword}\\([^)]*\\):'
    if re.search(pattern, content):
        match = re.search(pattern, content)
        line_num = content[:match.start()].count('\n') + 1
        print(f"  ✅ Encontrado: {match.group(0)} en línea {line_num}")

# Ver si hay un método que llame a motion_states
print("\n🔍 Métodos que usan motion_states:")
lines = content.split('\n')
for i, line in enumerate(lines):
    if 'motion_states' in line and 'def ' in lines[max(0, i-5):i+1]:
        # Buscar el def más cercano
        for j in range(max(0, i-5), i+1):
            if lines[j].strip().startswith('def '):
                print(f"  L{j+1}: {lines[j].strip()}")
                break

# Crear script para arreglar el método correcto
fix_code = '''# === fix_engine_update_correct.py ===
import os
import shutil
from datetime import datetime

print("🔧 Buscando y arreglando el método de actualización del engine...")

file_path = "trajectory_hub/core/enhanced_trajectory_engine.py"

with open(file_path, 'r') as f:
    content = f.read()

# Lista de posibles nombres del método
possible_methods = ['update', 'step', 'tick', 'process', '_update', '_step']
found_method = None

for method_name in possible_methods:
    pattern = f'def {method_name}\\(self.*?\\):'
    if re.search(pattern, content):
        found_method = method_name
        print(f"✅ Encontrado método: {found_method}")
        break

if not found_method:
    print("❌ No se encontró ningún método de actualización")
    exit(1)

print(f"📝 El método de actualización es: {found_method}")
'''

with open("fix_engine_update_correct.py", "w") as f:
    f.write(fix_code)

print("\n✅ Script creado: fix_engine_update_correct.py")