#!/usr/bin/env python3
"""
🔧 Fix: Problema de indentación en sphere
⚡ Busca y corrige la estructura completa
"""

import os

engine_path = "trajectory_hub/core/enhanced_trajectory_engine.py"

with open(engine_path, 'r') as f:
    lines = f.readlines()

print("🔍 Buscando estructura de formaciones...")

# Buscar el bloque de formaciones
formation_block_start = None
for i, line in enumerate(lines):
    if 'if formation == "circle"' in line:
        formation_block_start = i
        print(f"📍 Bloque formaciones empieza en línea {i+1}")
        break

if formation_block_start:
    # Obtener la indentación correcta
    indent = len(lines[formation_block_start]) - len(lines[formation_block_start].lstrip())
    print(f"   Indentación: {indent} espacios")
    
    # Buscar sphere y corregir indentación
    for i in range(formation_block_start, min(formation_block_start + 200, len(lines))):
        if 'elif formation == "sphere"' in lines[i]:
            current_indent = len(lines[i]) - len(lines[i].lstrip())
            if current_indent != indent:
                print(f"❌ Línea {i+1} tiene indentación incorrecta: {current_indent} vs {indent}")
                # Corregir esta línea y las siguientes del bloque
                lines[i] = ' ' * indent + lines[i].lstrip()
                
                # Corregir las líneas siguientes del bloque sphere
                j = i + 1
                while j < len(lines) and (lines[j].strip() == '' or len(lines[j]) - len(lines[j].lstrip()) > indent):
                    if lines[j].strip():  # No es línea vacía
                        # Ajustar indentación relativa
                        old_indent = len(lines[j]) - len(lines[j].lstrip())
                        relative_indent = old_indent - current_indent
                        new_indent = indent + relative_indent
                        if new_indent >= 0:
                            lines[j] = ' ' * new_indent + lines[j].lstrip()
                    j += 1
                
                print(f"✅ Corregida indentación de líneas {i+1} a {j}")
                break
    
    # Guardar
    with open(engine_path, 'w') as f:
        f.writelines(lines)
    
    print("\n📋 Verificando estructura:")
    # Mostrar todas las formaciones
    for i, line in enumerate(lines[formation_block_start:formation_block_start+100]):
        if 'formation ==' in line:
            print(f"   Línea {formation_block_start+i+1}: {line.rstrip()}")

else:
    print("❌ No se encontró el bloque de formaciones")
    print("\n🔍 Buscando 'elif formation'...")
    
    # Buscar cualquier elif formation
    for i, line in enumerate(lines):
        if 'elif formation' in line:
            print(f"   Línea {i+1}: {repr(line)}")
            # Mostrar contexto
            print("   Contexto:")
            for j in range(max(0, i-5), min(i+3, len(lines))):
                print(f"     {j+1}: {lines[j]}", end='')