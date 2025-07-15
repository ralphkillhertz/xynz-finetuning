# === diagnose_macro_trajectory_system.py ===
# 🔍 Diagnóstico completo para encontrar el sistema de trayectorias macro
# ⚡ Análisis profundo de la arquitectura

import os
import ast
import re

print("🔍 DIAGNÓSTICO PROFUNDO: Sistema de Trayectorias Macro\n")

# 1. Buscar en todos los archivos Python
print("1️⃣ BUSCANDO ARCHIVOS RELEVANTES...")
trajectory_files = []
macro_files = []
motion_files = []

for root, dirs, files in os.walk("trajectory_hub"):
    # Saltar __pycache__
    if "__pycache__" in root:
        continue
        
    for file in files:
        if file.endswith(".py"):
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Buscar referencias a trayectorias macro
                if any(term in content.lower() for term in ['macrotrajectory', 'macro_trajectory', 'set_macro_trajectory']):
                    trajectory_files.append(filepath)
                    
                # Buscar referencias a macros en general
                if 'macro' in content.lower() and 'create_macro' in content:
                    macro_files.append(filepath)
                    
                # Buscar motion_components
                if 'motion' in file.lower() or 'component' in file.lower():
                    motion_files.append(filepath)
                    
            except Exception as e:
                pass

print(f"\n📁 Archivos con referencias a trayectorias macro: {len(trajectory_files)}")
for f in trajectory_files[:5]:
    print(f"  - {f}")

# 2. Analizar motion_components.py
print("\n2️⃣ ANALIZANDO motion_components.py...")
mc_path = "trajectory_hub/core/motion_components.py"
if os.path.exists(mc_path):
    with open(mc_path, 'r') as f:
        content = f.read()
    
    # Buscar todas las clases
    classes = re.findall(r'class\s+(\w+).*?:', content)
    print(f"\n🔸 Clases encontradas en motion_components.py:")
    for cls in classes:
        print(f"  - {cls}")
        
    # Buscar enums de tipos de trayectoria
    trajectory_types = re.findall(r'class\s+(\w*Trajectory\w*).*?:', content)
    print(f"\n🔸 Clases relacionadas con trayectorias:")
    for tt in trajectory_types:
        print(f"  - {tt}")

# 3. Analizar enhanced_trajectory_engine.py
print("\n3️⃣ ANALIZANDO enhanced_trajectory_engine.py...")
engine_path = "trajectory_hub/core/enhanced_trajectory_engine.py"
if os.path.exists(engine_path):
    with open(engine_path, 'r') as f:
        content = f.read()
    
    # Buscar método set_macro_trajectory
    if "set_macro_trajectory" in content:
        print("✅ Encontrado método set_macro_trajectory")
        
        # Extraer el método
        method_match = re.search(r'def set_macro_trajectory\(self.*?\):\s*\n(.*?)(?=\n    def|\nclass|\Z)', 
                                content, re.DOTALL)
        if method_match:
            method_body = method_match.group(1)[:500]  # Primeras líneas
            print("\n📝 Implementación de set_macro_trajectory:")
            print("  " + method_body.replace("\n", "\n  ")[:300] + "...")
            
            # Buscar qué tipo de componente crea
            component_creation = re.search(r'(\w+)\s*=\s*\w+\(.*?\)', method_body)
            if component_creation:
                print(f"\n🎯 Parece crear: {component_creation.group(0)}")

# 4. Buscar en el proyecto cómo se implementan las trayectorias macro
print("\n4️⃣ BUSCANDO IMPLEMENTACIÓN DE TRAYECTORIAS MACRO...")

# Buscar patrones específicos
patterns_to_search = [
    r'trajectory.*=.*MacroTrajectory',
    r'self\.trajectory_type\s*=',
    r'macro.*trajectory.*component',
    r'def.*calculate.*trajectory.*macro',
    r'class.*Macro.*Component'
]

implementations = {}
for root, dirs, files in os.walk("trajectory_hub"):
    if "__pycache__" in root:
        continue
        
    for file in files:
        if file.endswith(".py"):
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r') as f:
                    content = f.read()
                    
                for pattern in patterns_to_search:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        if filepath not in implementations:
                            implementations[filepath] = []
                        implementations[filepath].extend(matches)
            except:
                pass

print("\n🔍 Implementaciones encontradas:")
for filepath, matches in implementations.items():
    print(f"\n📄 {filepath}:")
    for match in matches[:3]:
        print(f"  - {match}")

# 5. Analizar la estructura real
print("\n5️⃣ ANÁLISIS DE ESTRUCTURA REAL...")

# Buscar cómo se almacenan las trayectorias en los motion_states
if os.path.exists(engine_path):
    with open(engine_path, 'r') as f:
        content = f.read()
        
    # Buscar referencias a motion_states y active_components
    motion_refs = re.findall(r'motion.*active_components.*\[.*?\].*=', content)
    print("\n🔸 Referencias a active_components:")
    for ref in motion_refs[:5]:
        print(f"  - {ref}")

# 6. Verificar si las trayectorias macro están implementadas de otra forma
print("\n6️⃣ VERIFICANDO IMPLEMENTACIÓN ALTERNATIVA...")

# Tal vez no hay una clase MacroTrajectory separada
# Buscar si se usa la misma IndividualTrajectory para macros
individual_usage = []
if os.path.exists(engine_path):
    with open(engine_path, 'r') as f:
        lines = f.readlines()
        
    for i, line in enumerate(lines):
        if 'IndividualTrajectory' in line and 'macro' in lines[max(0,i-5):i+5]:
            individual_usage.append((i, line.strip()))

if individual_usage:
    print("\n⚠️ Posible uso de IndividualTrajectory para macros:")
    for line_num, line in individual_usage[:3]:
        print(f"  Línea {line_num}: {line}")

# Resumen final
print("\n" + "="*60)
print("📊 RESUMEN DEL DIAGNÓSTICO:")
print("="*60)

print("\n🔍 HALLAZGOS CLAVE:")
print("1. El sistema tiene métodos set_macro_trajectory")
print("2. Pero NO existe una clase MacroTrajectory separada")
print("3. Posiblemente usa IndividualTrajectory para todo")
print("4. O las trayectorias macro se implementan de otra forma")

print("\n🎯 RECOMENDACIÓN:")
print("Necesitamos ver la implementación exacta de set_macro_trajectory")
print("para entender cómo migrar correctamente.")