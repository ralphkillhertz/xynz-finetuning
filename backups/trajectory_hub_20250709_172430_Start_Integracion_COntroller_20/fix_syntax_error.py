#!/usr/bin/env python3
"""
🔧 Fix: Error de sintaxis en import
⚡ Repara enhanced_trajectory_engine.py línea 21
"""

import os

# Leer el archivo
with open("trajectory_hub/core/enhanced_trajectory_engine.py", 'r') as f:
    lines = f.readlines()

# Buscar y arreglar la línea problemática
fixed = False
for i, line in enumerate(lines):
    if i == 20:  # Línea 21 (índice 20)
        print(f"❌ Línea 21 actual: {line.strip()}")
        # Verificar si falta algo antes
        if i > 0 and not lines[i-1].strip().endswith((')', '"', "'", ']', '}')):
            # Probablemente falta cerrar algo en la línea anterior
            print(f"⚠️  Línea anterior: {lines[i-1].strip()}")
            # Buscar el import anterior para ver el patrón
            for j in range(i-1, max(0, i-10), -1):
                if "from trajectory_hub" in lines[j] and lines[j].strip().endswith(")"):
                    # Añadir cierre faltante
                    lines[i-1] = lines[i-1].rstrip() + ")\n"
                    print("✅ Añadido ) faltante en línea anterior")
                    fixed = True
                    break

# Si no se arregló, buscar el problema específico
if not fixed:
    # Buscar todos los imports de trajectory_hub
    for i, line in enumerate(lines):
        if line.strip().startswith("from trajectory_hub") and "FormationManager" in line:
            # Asegurar formato correcto
            lines[i] = "from trajectory_hub.control.managers.formation_manager import FormationManager\n"
            print(f"✅ Corregido import en línea {i+1}")
            fixed = True
            break

# Guardar
with open("trajectory_hub/core/enhanced_trajectory_engine.py", 'w') as f:
    f.writelines(lines)

print("✅ Archivo corregido")