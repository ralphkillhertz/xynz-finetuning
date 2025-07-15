#!/usr/bin/env python3
# 🔧 Fix: Eliminar límite hardcodeado de 16 sources
# ⚡ Líneas modificadas: 47, 58, 79 en spat_osc_bridge.py
# 🎯 Impacto: ALTO - Permite sources ilimitadas

import os
import shutil
from datetime import datetime

def fix_osc_limit():
    print("\n🔧 ELIMINANDO LÍMITE DE 16 SOURCES")
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
    
    # Arreglar líneas
    changes = 0
    for i, line in enumerate(lines):
        # Cambiar n_sources a 128 (o más si necesitas)
        if 'self.n_sources = 16' in line:
            lines[i] = line.replace('16', '128')
            print(f"✅ Línea {i+1}: n_sources aumentado a 128")
            changes += 1
            
        # Cambiar la condición para usar <= en lugar de 
        elif 'if 0 <= source_id < self.n_sources:' in line:
            lines[i] = line.replace('< self.n_sources', '<= self.n_sources')
            print(f"✅ Línea {i+1}: Condición cambiada a <=")
            changes += 1
    
    if changes > 0:
        # Escribir cambios
        with open(file_path, 'w') as f:
            f.writelines(lines)
        
        print(f"\n✅ {changes} cambios aplicados")
        print("\n🎯 Ahora soporta hasta 128 sources")
        print("⚡ Ejecuta el test nuevamente para verificar")
    else:
        print("⚠️ No se encontraron las líneas a modificar")

if __name__ == "__main__":
    fix_osc_limit()