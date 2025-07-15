#!/usr/bin/env python3
"""
🧪 TEST STANDALONE DE CONCENTRACIÓN
⚡ Prueba sin imports complejos
"""

import os
import sys
import numpy as np

# Agregar rutas
sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('trajectory_hub'))

print("=" * 60)
print("🧪 TEST DE CONCENTRACIÓN")
print("=" * 60)

# Intentar importar de diferentes maneras
imported = False

# Opción 1: trajectory_hub.core
try:
    from trajectory_hub.core.motion_components import SourceMotion, MotionState
    from trajectory_hub.core.rotation_system import Concentration, ConcentrationMode
    print("✅ Import método 1 exitoso")
    imported = True
except Exception as e:
    print(f"❌ Import método 1 falló: {e}")

# Opción 2: core directo
if not imported:
    try:
        from core.motion_components import SourceMotion, MotionState
        from core.rotation_system import Concentration, ConcentrationMode
        print("✅ Import método 2 exitoso")
        imported = True
    except Exception as e:
        print(f"❌ Import método 2 falló: {e}")

# Opción 3: buscar el controlador principal
if not imported:
    print("\n🔍 Buscando controlador principal...")
    for root, dirs, files in os.walk("."):
        if "backup" in root:
            continue
        for file in files:
            if file.endswith("_controller.py") or file == "main.py":
                filepath = os.path.join(root, file)
                print(f"   Encontrado: {filepath}")
                
                # Verificar si tiene opción 31
                try:
                    with open(filepath, 'r') as f:
                        if "'31'" in f.read():
                            print(f"   ✅ Contiene opción 31!")
                            
                            # Ejecutar directamente
                            print(f"\n⚡ SOLUCIÓN: Ejecuta directamente:")
                            print(f"   python {filepath}")
                            print("   Luego selecciona opción 31")
                except:
                    pass

# Si logramos importar, hacer test
if imported:
    print("\n📊 EJECUTANDO TEST...")
    
    try:
        # Crear motion
        motion = SourceMotion(source_id=0)
        motion.state.position = np.array([5.0, 0.0, 0.0])
        
        # Crear concentration
        concentration = Concentration()
        concentration.enabled = True
        concentration.factor = 0.0  # Máxima concentración
        concentration.target = np.array([0.0, 0.0, 0.0])
        
        print(f"Posición inicial: {motion.state.position}")
        
        # Aplicar
        if hasattr(concentration, 'apply'):
            concentration.apply(motion)
            print(f"Posición después: {motion.state.position}")
            
            dist = np.linalg.norm(motion.state.position)
            if dist < 4.9:
                print("✅ ¡Concentración funciona!")
            else:
                print("❌ Concentración no se aplicó")
        else:
            print("❌ Concentration no tiene método apply")
        
    except Exception as e:
        print(f"❌ Error en test: {e}")

# Instrucciones finales
print("\n" + "=" * 60)
print("PRÓXIMOS PASOS:")
print("=" * 60)
print("1. Ejecuta: python deep_search.py")
print("2. Ejecuta: python fix_motion_direct.py")
print("3. Busca el archivo del controlador principal")
print("4. Reinicia y prueba opción 31")
print("=" * 60)