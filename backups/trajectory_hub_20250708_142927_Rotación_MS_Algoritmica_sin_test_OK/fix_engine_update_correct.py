# === fix_engine_update_correct.py ===
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
    pattern = f'def {method_name}\(self.*?\):'
    if re.search(pattern, content):
        found_method = method_name
        print(f"✅ Encontrado método: {found_method}")
        break

if not found_method:
    print("❌ No se encontró ningún método de actualización")
    exit(1)

print(f"📝 El método de actualización es: {found_method}")
