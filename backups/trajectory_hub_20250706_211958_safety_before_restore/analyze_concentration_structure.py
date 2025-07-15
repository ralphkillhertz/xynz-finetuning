#!/usr/bin/env python3
"""
🔍 ANÁLISIS DETALLADO DE ConcentrationComponent
"""

import os
import re

print("=" * 80)
print("🔍 ANÁLISIS DETALLADO DE CONCENTRATION")
print("=" * 80)

# Leer el archivo
motion_file = "trajectory_hub/core/motion_components.py"

with open(motion_file, 'r') as f:
    content = f.read()
    lines = content.split('\n')

# 1. Encontrar la clase ConcentrationComponent
print("\n1️⃣ ESTRUCTURA DE ConcentrationComponent:")
print("-" * 60)

class_start = -1
class_end = -1

for i, line in enumerate(lines):
    if 'class ConcentrationComponent' in line:
        class_start = i
        print(f"Línea {i+1}: {line}")
        
        # Buscar el final de la clase
        indent_level = len(line) - len(line.lstrip())
        
        for j in range(i+1, len(lines)):
            if lines[j].strip() and not lines[j].startswith(' '):
                class_end = j
                break
            elif lines[j].startswith('class '):
                class_end = j
                break
        
        if class_end == -1:
            class_end = len(lines)
        
        break

if class_start >= 0:
    # Extraer métodos
    print(f"\nClase encontrada: líneas {class_start+1} a {class_end+1}")
    
    print("\n📋 MÉTODOS:")
    for i in range(class_start, class_end):
        if lines[i].strip().startswith('def '):
            # Mostrar método con sus primeras líneas
            print(f"\n  Línea {i+1}: {lines[i]}")
            # Mostrar siguientes 5 líneas
            for j in range(i+1, min(i+6, class_end)):
                if lines[j].strip():
                    print(f"  Línea {j+1}: {lines[j][:80]}")

# 2. Buscar cómo se integra con SourceMotion
print("\n\n2️⃣ INTEGRACIÓN CON SourceMotion:")
print("-" * 60)

# Buscar SourceMotion
source_motion_start = -1
for i, line in enumerate(lines):
    if 'class SourceMotion' in line:
        source_motion_start = i
        print(f"SourceMotion encontrado en línea {i+1}")
        break

# Buscar referencias a concentration en SourceMotion
if source_motion_start >= 0:
    print("\nReferencias a concentration en SourceMotion:")
    
    for i in range(source_motion_start, min(source_motion_start + 200, len(lines))):
        if 'concentration' in lines[i].lower():
            print(f"  Línea {i+1}: {lines[i].strip()[:80]}")

# 3. Buscar cómo se aplican los componentes
print("\n\n3️⃣ SISTEMA DE COMPONENTES:")
print("-" * 60)

# Buscar el método update de SourceMotion
for i in range(source_motion_start, len(lines)):
    if lines[i].strip().startswith('def update('):
        print(f"\nSourceMotion.update() en línea {i+1}:")
        
        # Mostrar cómo se aplican componentes
        for j in range(i, min(i+30, len(lines))):
            if 'component' in lines[j].lower():
                print(f"  Línea {j+1}: {lines[j].strip()[:80]}")
        break

# 4. Buscar la interfaz base de componentes
print("\n\n4️⃣ INTERFAZ BASE DE COMPONENTES:")
print("-" * 60)

# Buscar MotionComponent base class
for i, line in enumerate(lines):
    if 'class MotionComponent' in line and 'ABC' in line:
        print(f"\nMotionComponent base encontrado en línea {i+1}")
        
        # Mostrar métodos abstractos
        for j in range(i, min(i+50, len(lines))):
            if '@abstractmethod' in lines[j] or 'def ' in lines[j]:
                print(f"  Línea {j+1}: {lines[j].strip()}")
        break

# 5. Ejemplo de uso
print("\n\n5️⃣ CÓMO SE USA ConcentrationComponent:")
print("-" * 60)

# Buscar inicializaciones o usos
concentration_uses = []
for i, line in enumerate(lines):
    if 'ConcentrationComponent(' in line or 'concentration' in line.lower():
        if i not in range(class_start, class_end):  # Fuera de la definición de clase
            concentration_uses.append((i+1, line.strip()[:100]))

print(f"\nUsos encontrados: {len(concentration_uses)}")
for line_num, usage in concentration_uses[:10]:
    print(f"  Línea {line_num}: {usage}")

# Guardar análisis
print("\n\n💾 Guardando análisis completo...")
with open("concentration_analysis_detailed.txt", 'w') as f:
    f.write("ANÁLISIS DETALLADO DE ConcentrationComponent\n")
    f.write("=" * 80 + "\n\n")
    
    if class_start >= 0:
        f.write("CLASE COMPLETA:\n")
        f.write("-" * 40 + "\n")
        for i in range(class_start, class_end):
            f.write(f"{i+1:4d}: {lines[i]}\n")

print("✅ Análisis guardado en: concentration_analysis_detailed.txt")
print("=" * 80)