#!/usr/bin/env python3
"""
🔧 Fix: Error sintaxis en sphere línea 544
⚡ Revisa contexto y corrige
"""

import os

engine_path = "trajectory_hub/core/enhanced_trajectory_engine.py"

# Leer archivo
with open(engine_path, 'r') as f:
    lines = f.readlines()

# Buscar línea 544 y contexto
print("📍 Contexto líneas 540-550:")
for i in range(539, min(550, len(lines))):
    print(f"{i+1}: {lines[i]}", end='')

# Buscar el problema - probablemente falta cerrar algo
for i in range(543, 535, -1):  # Revisar hacia atrás
    line = lines[i].rstrip()
    if line and not line.endswith((':',)):
        # Verificar si es una línea que debería terminar con :
        if any(keyword in line for keyword in ['if', 'elif', 'else', 'for', 'while', 'def', 'class']):
            if not line.endswith(':'):
                print(f"\n❌ Línea {i+1} falta ':' al final")
                lines[i] = line + ':\n'
                break
        # Verificar paréntesis/corchetes sin cerrar
        open_count = line.count('(') - line.count(')')
        if open_count > 0:
            print(f"\n❌ Línea {i+1} tiene paréntesis sin cerrar")
            # Buscar dónde cerrar
            for j in range(i+1, min(i+5, len(lines))):
                if 'elif' in lines[j]:
                    # Añadir cierre antes del elif
                    lines[i] = lines[i].rstrip() + ')\n'
                    print(f"✅ Añadido ) al final de línea {i+1}")
                    break
            break

# Guardar
with open(engine_path, 'w') as f:
    f.writelines(lines)

print("\n✅ Archivo corregido")

# Mostrar contexto corregido
print("\n📋 Nuevo contexto:")
with open(engine_path, 'r') as f:
    lines = f.readlines()
for i in range(540, min(548, len(lines))):
    print(f"{i+1}: {lines[i]}", end='')