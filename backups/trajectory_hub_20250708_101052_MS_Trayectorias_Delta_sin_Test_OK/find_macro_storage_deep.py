# === find_macro_storage_deep.py ===
# 🔍 Encontrar EXACTAMENTE dónde y cómo se almacenan los macros
# ⚡ Crítico para arreglar el sistema

import re
import ast

print("🔍 BÚSQUEDA PROFUNDA: Sistema de Macros\n")

engine_path = "trajectory_hub/core/enhanced_trajectory_engine.py"

with open(engine_path, 'r') as f:
    content = f.read()
    lines = content.split('\n')

# 1. Buscar TODAS las referencias a macros
print("1️⃣ TODAS LAS REFERENCIAS A MACROS:")
macro_patterns = [
    r'self\.\w*macro\w*',
    r'_macro\w*',
    r'macro\w*\s*=',
    r'\.macro\w*',
]

found_attrs = set()
for pattern in macro_patterns:
    matches = re.findall(pattern, content)
    found_attrs.update(matches)

for attr in sorted(found_attrs)[:20]:
    print(f"  - {attr}")

# 2. Buscar en __init__
print("\n2️⃣ EN __init__:")
init_match = re.search(r'def __init__\(.*?\):.*?(?=\n    def)', content, re.DOTALL)
if init_match:
    init_content = init_match.group(0)
    # Buscar inicializaciones de diccionarios
    dict_inits = re.findall(r'self\.(\w+)\s*=\s*\{\}', init_content)
    print("  Diccionarios inicializados:")
    for d in dict_inits:
        print(f"    - self.{d} = {{}}")

# 3. Buscar el método create_macro completo
print("\n3️⃣ MÉTODO create_macro COMPLETO:")
create_match = re.search(r'def create_macro\(.*?\):.*?(?=\n    def|\Z)', content, re.DOTALL)
if create_match:
    method = create_match.group(0)
    # Mostrar líneas relevantes
    lines = method.split('\n')
    for i, line in enumerate(lines[:50]):  # Primeras 50 líneas
        if any(word in line for word in ['macro', 'Macro', 'trajectory', 'component', 'source', 'motion']):
            print(f"  {i:3d}: {line}")

# 4. Buscar clase Macro si existe
print("\n4️⃣ BUSCANDO CLASE Macro:")
class_matches = re.findall(r'class (\w*[Mm]acro\w*)', content)
for cls in class_matches:
    print(f"  - {cls}")

# 5. Buscar en imports
print("\n5️⃣ IMPORTS RELACIONADOS:")
import_lines = [line for line in lines if 'import' in line and 'macro' in line.lower()]
for line in import_lines:
    print(f"  - {line.strip()}")

# 6. Buscar archivos que puedan tener la definición de Macro
print("\n6️⃣ BUSCANDO DEFINICIÓN DE MACRO EN OTROS ARCHIVOS:")
import os
for root, dirs, files in os.walk("trajectory_hub"):
    if "__pycache__" in root:
        continue
    
    for file in files:
        if file.endswith(".py"):
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r') as f:
                    file_content = f.read()
                
                # Buscar class Macro
                if re.search(r'class Macro[^a-z]', file_content):
                    print(f"  ✅ Encontrado en: {filepath}")
                    
                    # Mostrar la definición
                    class_def = re.search(r'(class Macro.*?\n(?:    .*\n)*)', file_content)
                    if class_def:
                        print("  Definición:")
                        for line in class_def.group(1).split('\n')[:10]:
                            print(f"    {line}")
            except:
                pass

# 7. Verificar si los motion_states se actualizan correctamente
print("\n7️⃣ CÓMO SE AÑADEN COMPONENTES A motion_states:")
# Buscar patrones de añadir componentes
component_patterns = [
    r'motion.*active_components.*\[.*?\]\s*=',
    r'\.active_components\[.*?\]\s*=',
    r'active_components.*=.*\{',
]

for pattern in component_patterns:
    matches = re.findall(pattern + r'.*', content)
    if matches:
        print(f"\n  Patrón: {pattern}")
        for match in matches[:3]:
            print(f"    - {match.strip()}")

print("\n" + "="*60)
print("ANÁLISIS COMPLETO - Próximo paso: crear fix basado en hallazgos")