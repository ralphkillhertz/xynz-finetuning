#!/usr/bin/env python3
"""
🔍 BÚSQUEDA PROFUNDA DE ARCHIVOS
⚡ Encuentra engine y concentration
"""

import os
import re

print("=" * 60)
print("🔍 BÚSQUEDA PROFUNDA")
print("=" * 60)

# Buscar archivos que contengan clases/funciones clave
key_patterns = {
    "engine": [
        r"class.*Engine",
        r"def update\(self.*\).*:",
        r"self\._positions",
        r"self\._source_motions"
    ],
    "concentration": [
        r"class.*Concentration",
        r"def.*concentration",
        r"ConcentrationMode",
        r"concentration_factor",
        r"def _apply_concentration"
    ],
    "main_controller": [
        r"if __name__ == .__main__.",
        r"OSCController",
        r"menu.*31.*oncentra"
    ]
}

found_files = {
    "engine": [],
    "concentration": [],
    "main_controller": []
}

# Buscar en todos los archivos .py
for root, dirs, files in os.walk("."):
    # Ignorar backups y directorios ocultos
    if "backup" in root or "/." in root or "__pycache__" in root:
        continue
    
    for file in files:
        if file.endswith(".py"):
            filepath = os.path.join(root, file)
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Buscar patrones
                for category, patterns in key_patterns.items():
                    for pattern in patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            if filepath not in found_files[category]:
                                found_files[category].append(filepath)
                            break
            except:
                pass

# Mostrar resultados
print("\n🎯 ARCHIVOS PRINCIPALES ENCONTRADOS:")
print("-" * 60)

for category, files in found_files.items():
    if files:
        print(f"\n📁 {category.upper()}:")
        for f in files[:5]:  # Mostrar máximo 5
            print(f"   ✅ {f}")
            
            # Analizar contenido
            with open(f, 'r', encoding='utf-8') as file:
                content = file.read()
                
            if category == "engine":
                if "class SpatialEngine" in content:
                    print("      → Define SpatialEngine")
                if "class TrajectoryEngine" in content:
                    print("      → Define TrajectoryEngine")
                if "_positions[" in content:
                    print("      → Maneja _positions[]")
                    
            elif category == "concentration":
                if "enabled" in content and "factor" in content:
                    print("      → Parece ser el módulo correcto")
                if "31" in content:
                    print("      → Contiene opción 31")

# Buscar específicamente archivos con "31" (opción de concentración)
print("\n🔍 ARCHIVOS CON OPCIÓN 31 (CONCENTRACIÓN):")
print("-" * 60)

option_31_files = []
for root, dirs, files in os.walk("."):
    if "backup" in root or "/." in root:
        continue
    
    for file in files:
        if file.endswith(".py"):
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r') as f:
                    content = f.read()
                if "'31'" in content or '"31"' in content or "== 31" in content:
                    if "concentra" in content.lower():
                        option_31_files.append(filepath)
            except:
                pass

for f in option_31_files[:3]:
    print(f"   ✅ {f}")

# Listar estructura de directorios principales
print("\n📂 ESTRUCTURA DE DIRECTORIOS:")
print("-" * 60)

for item in os.listdir("."):
    if os.path.isdir(item) and not item.startswith('.') and item != "backups":
        print(f"\n{item}/:")
        try:
            subitems = os.listdir(item)
            for subitem in sorted(subitems)[:10]:
                if os.path.isdir(os.path.join(item, subitem)):
                    print(f"  📁 {subitem}/")
                elif subitem.endswith('.py'):
                    print(f"  📄 {subitem}")
        except:
            pass

print("\n" + "=" * 60)