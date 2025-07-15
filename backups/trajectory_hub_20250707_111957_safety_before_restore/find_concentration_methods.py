#!/usr/bin/env python3
"""
🔍 BUSCAR MÉTODOS DE CONCENTRACIÓN
📍 Encuentra cómo está implementada la concentración en el proyecto
"""

import os
import re
from pathlib import Path

print("🔍 BUSCANDO IMPLEMENTACIÓN DE CONCENTRACIÓN")
print("="*60)

# Palabras clave relacionadas con concentración
keywords = [
    'concentra', 'concentrate', 'focus', 'converge', 'gather',
    'concentration_factor', 'concentration_mode', 'apply_concentration'
]

found_methods = {}
found_in_files = []

# Buscar en todos los archivos Python
for root, dirs, files in os.walk("trajectory_hub"):
    # Ignorar directorios de cache y backups
    if '__pycache__' in root or 'backup' in root:
        continue
        
    for file in files:
        if file.endswith('.py'):
            filepath = os.path.join(root, file)
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Buscar keywords
                for keyword in keywords:
                    if keyword.lower() in content.lower():
                        # Buscar definiciones de métodos con este keyword
                        pattern = rf'def\s+(\w*{keyword}\w*)\s*\('
                        methods = re.findall(pattern, content, re.IGNORECASE)
                        
                        if methods:
                            if filepath not in found_methods:
                                found_methods[filepath] = []
                            found_methods[filepath].extend(methods)
                            
                        # También buscar atributos y variables
                        if keyword in content:
                            found_in_files.append((filepath, keyword))
                            
            except Exception as e:
                print(f"⚠️ Error leyendo {filepath}: {e}")

# Mostrar resultados
print("\n📋 MÉTODOS ENCONTRADOS:")
print("-"*60)

if found_methods:
    for filepath, methods in found_methods.items():
        print(f"\n📄 {os.path.relpath(filepath)}:")
        for method in set(methods):  # Eliminar duplicados
            print(f"   - def {method}()")
else:
    print("❌ No se encontraron métodos con keywords de concentración")

# Buscar específicamente en enhanced_trajectory_engine.py
print("\n\n🔍 MÉTODOS EN ENHANCED_TRAJECTORY_ENGINE:")
print("-"*60)

engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"
if os.path.exists(engine_file):
    with open(engine_file, 'r') as f:
        content = f.read()
    
    # Buscar TODOS los métodos públicos
    all_methods = re.findall(r'def\s+([^_]\w*)\s*\(self', content)
    
    # Filtrar métodos que podrían estar relacionados
    relevant_methods = []
    for method in all_methods:
        # Buscar métodos que contengan keywords relevantes
        if any(kw in method.lower() for kw in ['set', 'apply', 'concentration', 'focus', 'converge']):
            relevant_methods.append(method)
    
    if relevant_methods:
        print("Métodos públicos potencialmente relevantes:")
        for method in relevant_methods:
            print(f"   - {method}()")
    
    # Buscar en el contenido del método si menciona concentración
    print("\n🔍 Buscando referencias a concentración en el código...")
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'concentra' in line.lower() and not line.strip().startswith('#'):
            print(f"   Línea {i+1}: {line.strip()[:80]}...")

# Buscar en el controlador interactivo
print("\n\n🔍 OPCIONES EN INTERACTIVE_CONTROLLER:")
print("-"*60)

controller_file = "trajectory_hub/interface/interactive_controller.py"
if os.path.exists(controller_file):
    with open(controller_file, 'r') as f:
        content = f.read()
    
    # Buscar menú con opciones de concentración
    lines = content.split('\n')
    in_menu = False
    menu_lines = []
    
    for line in lines:
        if 'concentración' in line.lower() or 'concentration' in line.lower():
            # Mostrar contexto
            idx = lines.index(line)
            context_start = max(0, idx - 2)
            context_end = min(len(lines), idx + 3)
            
            print(f"\nEncontrado en línea {idx+1}:")
            for i in range(context_start, context_end):
                print(f"   {lines[i]}")

# Buscar imports relacionados
print("\n\n🔍 IMPORTS RELACIONADOS:")
print("-"*60)

for root, dirs, files in os.walk("trajectory_hub"):
    if '__pycache__' in root:
        continue
        
    for file in files:
        if file.endswith('.py'):
            filepath = os.path.join(root, file)
            
            try:
                with open(filepath, 'r') as f:
                    lines = f.readlines()
                    
                for line in lines:
                    if 'import' in line and any(kw in line.lower() for kw in ['concentra', 'focus']):
                        print(f"{os.path.relpath(filepath)}: {line.strip()}")
                        
            except:
                pass

print("\n✅ Búsqueda completada")