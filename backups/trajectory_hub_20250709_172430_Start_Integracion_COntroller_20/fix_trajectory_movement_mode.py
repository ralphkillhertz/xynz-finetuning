#!/usr/bin/env python3
"""
🔧 Fix: TrajectoryMovementMode no definido
⚡ Define la clase o reemplaza su uso
"""

import os
import re

def fix_trajectory_mode():
    """Arregla el uso de TrajectoryMovementMode"""
    
    engine_path = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    print("🔍 Buscando uso de TrajectoryMovementMode...")
    
    # Leer archivo
    with open(engine_path, 'r') as f:
        lines = f.readlines()
    
    # Buscar dónde se usa
    uses = []
    for i, line in enumerate(lines):
        if "TrajectoryMovementMode" in line:
            uses.append((i+1, line.strip()))
            print(f"   Línea {i+1}: {line.strip()[:80]}...")
    
    print(f"\n📊 Encontrados {len(uses)} usos")
    
    # Opción 1: Definir la clase localmente si no existe
    # Buscar si ya está definida en el archivo
    class_defined = any("class TrajectoryMovementMode" in line for line in lines)
    
    if not class_defined:
        print("\n✅ Añadiendo definición de TrajectoryMovementMode...")
        
        # Buscar dónde insertar (después de imports, antes de la clase)
        insert_pos = 0
        for i, line in enumerate(lines):
            if line.startswith("class EnhancedTrajectoryEngine"):
                insert_pos = i
                break
            elif line.strip() and not line.startswith(("import", "from", "#")) and insert_pos == 0:
                # Después de los imports
                insert_pos = i
        
        # Definición simple
        mode_definition = '''
# Definición temporal de modos de movimiento
from enum import Enum

class TrajectoryMovementMode(Enum):
    """Modos de movimiento para trayectorias"""
    FIX = "fix"
    FREE = "free"
    ELASTIC = "elastic"

'''
        
        # Insertar
        lines.insert(insert_pos, mode_definition)
        print(f"   Insertado en línea {insert_pos+1}")
    
    # Guardar
    with open(engine_path, 'w') as f:
        f.writelines(lines)
    
    print("\n✅ Archivo actualizado")
    
    # Verificar
    print("\n🧪 Verificando...")
    try:
        import subprocess
        result = subprocess.run(
            ["python", "-c", "from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine; print('✅ Import exitoso')"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(result.stdout)
            return True
        else:
            print(f"❌ Error: {result.stderr}")
            
            # Si sigue fallando, buscar más problemas
            if "TrajectoryDisplacementMode" in result.stderr:
                print("\n⚠️  También falta TrajectoryDisplacementMode")
                return fix_displacement_mode()
            
            return False
            
    except Exception as e:
        print(f"❌ Error al verificar: {e}")
        return False

def fix_displacement_mode():
    """Arregla TrajectoryDisplacementMode si también falta"""
    
    engine_path = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    print("\n🔧 Añadiendo TrajectoryDisplacementMode...")
    
    with open(engine_path, 'r') as f:
        content = f.read()
    
    # Buscar donde está TrajectoryMovementMode
    mode_pos = content.find("class TrajectoryMovementMode")
    
    if mode_pos != -1:
        # Añadir después
        insert_pos = content.find("\n\n", mode_pos) + 2
        
        displacement_def = '''class TrajectoryDisplacementMode(Enum):
    """Modos de desplazamiento para trayectorias"""
    RELATIVE = "relative"
    ABSOLUTE = "absolute"
    POLAR = "polar"

'''
        
        content = content[:insert_pos] + displacement_def + content[insert_pos:]
        
        with open(engine_path, 'w') as f:
            f.write(content)
        
        print("✅ TrajectoryDisplacementMode añadido")
    
    return True

if __name__ == "__main__":
    print("🔧 FIX TRAJECTORY MOVEMENT MODE")
    print("=" * 50)
    
    if fix_trajectory_mode():
        print("\n✅ SISTEMA ARREGLADO")
        print("\n🎯 Ejecutar:")
        print("   python -m trajectory_hub.interface.interactive_controller")
    else:
        print("\n❌ Persisten errores")
        print("   Puede requerir más fixes")