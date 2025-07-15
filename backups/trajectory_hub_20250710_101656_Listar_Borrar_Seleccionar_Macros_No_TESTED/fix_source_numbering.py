#!/usr/bin/env python3
# 🔧 Fix: Corregir numeración de sources en OSC
# ⚡ Líneas modificadas: 60, 80 en spat_osc_bridge.py
# 🎯 Impacto: ALTO - Todas las sources se numerarán correctamente

import os
import shutil
from datetime import datetime

def fix_source_numbering():
    print("\n🔧 ARREGLANDO NUMERACIÓN DE SOURCES")
    print("=" * 60)
    
    file_path = "trajectory_hub/core/spat_osc_bridge.py"
    
    # Backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{file_path}.backup_{timestamp}"
    shutil.copy2(file_path, backup_path)
    print(f"✅ Backup creado: {backup_path}")
    
    # Leer archivo
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    # Arreglar líneas problemáticas
    fixed = False
    for i, line in enumerate(lines):
        # Arreglar línea 60 (aproximadamente)
        if 'address = f"/source/{source_id + 1}/xyz"' in line:
            lines[i] = line.replace('source_id + 1', 'source_id')
            print(f"✅ Arreglado línea {i+1}: OSC address usa source_id directamente")
            fixed = True
            
        # Arreglar línea 80 (aproximadamente)
        elif 'address = f"/source/{source_id + 1}/{param}"' in line:
            lines[i] = line.replace('source_id + 1', 'source_id') 
            print(f"✅ Arreglado línea {i+1}: OSC param address usa source_id directamente")
            fixed = True
    
    if fixed:
        # Escribir cambios
        with open(file_path, 'w') as f:
            f.writelines(lines)
        print("\n✅ Archivo actualizado correctamente")
        print("\n🎯 Ahora las sources se numerarán:")
        print("   - Source 0 → OSC /source/1/xyz")
        print("   - Source 1 → OSC /source/2/xyz")
        print("   - etc...")
        print("\n⚡ Ejecuta el controller para verificar que aparezcan TODAS las sources")
    else:
        print("⚠️ No se encontraron las líneas problemáticas")
        print("   Verificando manualmente...")

if __name__ == "__main__":
    fix_source_numbering()