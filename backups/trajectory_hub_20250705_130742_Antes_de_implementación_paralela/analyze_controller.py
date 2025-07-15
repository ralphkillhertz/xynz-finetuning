#!/usr/bin/env python3
"""
🔍 ANÁLISIS DEL CONTROLADOR
⚡ Examina interactive_controller.py
"""

import os
import re

print("=" * 70)
print("🔍 ANÁLISIS DE INTERACTIVE CONTROLLER")
print("=" * 70)

controller_path = "trajectory_hub/interface/interactive_controller.py"

if not os.path.exists(controller_path):
    print(f"❌ No existe: {controller_path}")
    exit(1)

with open(controller_path, 'r') as f:
    content = f.read()
    lines = content.split('\n')

print(f"✅ Archivo cargado: {len(lines)} líneas")

# 1. Buscar opción 31
print("\n📍 OPCIÓN 31 - CONCENTRACIÓN:")
print("-" * 50)

for i, line in enumerate(lines):
    if "'31'" in line or '"31"' in line:
        # Mostrar contexto
        start = max(0, i-2)
        end = min(len(lines), i+8)
        
        for j in range(start, end):
            marker = ">>>" if j == i else "   "
            print(f"{marker} {j+1:4d}: {lines[j][:80]}")
        print()

# 2. Buscar métodos de concentración
print("\n🔧 MÉTODOS DE CONCENTRACIÓN:")
print("-" * 50)

concentration_methods = []
for i, line in enumerate(lines):
    if re.search(r'def.*concentration', line, re.IGNORECASE):
        concentration_methods.append((i, line.strip()))
        print(f"   Línea {i+1}: {line.strip()}")

# 3. Buscar referencias al engine
print("\n⚙️ SISTEMA/ENGINE:")
print("-" * 50)

engine_refs = set()
for i, line in enumerate(lines):
    # Buscar self.algo que parezca un engine
    match = re.search(r'self\.(\w*(?:engine|system|hub|controller)\w*)', line, re.IGNORECASE)
    if match:
        engine_refs.add(match.group(1))

for ref in sorted(engine_refs):
    print(f"   self.{ref}")

# 4. Buscar cómo se accede a las posiciones
print("\n📊 ACCESO A POSICIONES:")
print("-" * 50)

position_patterns = [
    r'_positions\[',
    r'\.positions\[',
    r'\.position =',
    r'\.state\.position',
    r'get_positions',
    r'update_positions'
]

found_patterns = set()
for pattern in position_patterns:
    for i, line in enumerate(lines):
        if re.search(pattern, line):
            found_patterns.add(pattern)
            print(f"   Patrón '{pattern}' en línea {i+1}")
            break

# 5. Buscar imports relacionados
print("\n📦 IMPORTS RELEVANTES:")
print("-" * 50)

for i, line in enumerate(lines):
    if line.startswith('from') or line.startswith('import'):
        if any(word in line.lower() for word in ['motion', 'engine', 'concentration', 'spatial', 'trajectory']):
            print(f"   {line.strip()}")

# 6. Buscar la clase principal
print("\n🏗️ CLASE PRINCIPAL:")
print("-" * 50)

for i, line in enumerate(lines):
    if line.startswith('class '):
        class_name = re.search(r'class (\w+)', line)
        if class_name:
            print(f"   Línea {i+1}: {class_name.group(0)}")
            
            # Buscar __init__
            for j in range(i, min(i+50, len(lines))):
                if 'def __init__' in lines[j]:
                    print(f"   __init__ en línea {j+1}")
                    
                    # Ver qué se inicializa
                    for k in range(j, min(j+30, len(lines))):
                        if 'self.' in lines[k] and '=' in lines[k]:
                            var_match = re.search(r'self\.(\w+)\s*=', lines[k])
                            if var_match:
                                var_name = var_match.group(1)
                                if any(word in var_name.lower() for word in ['engine', 'hub', 'system']):
                                    print(f"      {lines[k].strip()[:60]}")
                    break
            break

print("\n" + "=" * 70)
print("DIAGNÓSTICO:")
print("=" * 70)

# Determinar arquitectura
if 'TrajectoryEngine' in content:
    print("✅ Usa TrajectoryEngine")
elif 'SpatialEngine' in content:
    print("✅ Usa SpatialEngine")
else:
    print("⚠️ Engine no identificado claramente")

# Verificar si concentration está implementada
if concentration_methods:
    print(f"✅ {len(concentration_methods)} métodos de concentración encontrados")
else:
    print("❌ No se encontraron métodos de concentración")

# Sugerir solución
print("\n⚡ PRÓXIMO PASO:")
print("   python fix_concentration_controller.py")
print("=" * 70)