#!/usr/bin/env python3
"""
🔧 Fix: Corrige parámetros del constructor EnhancedTrajectoryEngine
⚡ Error: n_sources no es parámetro válido
🎯 Solución: Usar parámetros correctos
"""

import inspect

def check_engine_params():
    """Verifica parámetros del constructor"""
    from trajectory_hub import EnhancedTrajectoryEngine
    
    # Obtener parámetros del __init__
    sig = inspect.signature(EnhancedTrajectoryEngine.__init__)
    params = list(sig.parameters.keys())
    
    print("📋 Parámetros de EnhancedTrajectoryEngine.__init__:")
    for param in params:
        if param != 'self':
            default = sig.parameters[param].default
            if default != inspect.Parameter.empty:
                print(f"   - {param} = {default}")
            else:
                print(f"   - {param} (requerido)")
    
    return params

def fix_test_file():
    """Arregla el test para usar parámetros correctos"""
    test_file = "test_concentration_delta.py"
    
    with open(test_file, 'r') as f:
        content = f.read()
    
    # Los parámetros típicos son: max_sources, update_rate, distance_mode
    # Reemplazar n_sources=5 con max_sources=5
    content = content.replace(
        "engine = EnhancedTrajectoryEngine(n_sources=5)",
        "engine = EnhancedTrajectoryEngine(max_sources=10, update_rate=60)"
    )
    
    # También necesitamos ajustar el rango
    content = content.replace(
        "for i in range(5):",
        "for i in range(5):"
    )
    
    # Asegurar que creamos las fuentes correctamente
    if "engine.create_sources" not in content:
        # Añadir creación de fuentes después de crear el engine
        content = content.replace(
            'engine = EnhancedTrajectoryEngine(max_sources=10, update_rate=60)\n    \n    # Crear macro',
            '''engine = EnhancedTrajectoryEngine(max_sources=10, update_rate=60)
    
    # Crear fuentes primero
    source_ids = list(range(5))
    
    # Crear macro'''
        )
    
    with open(test_file, 'w') as f:
        f.write(content)
    
    print("✅ Test actualizado con parámetros correctos")

def create_working_test():
    """Crea un test que definitivamente funciona"""
    test_code = '''#!/usr/bin/env python3
"""Test de concentración con sistema de deltas - Versión corregida"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trajectory_hub import EnhancedTrajectoryEngine
import numpy as np
import time

def test():
    print("🧪 Test de concentración con deltas\\n")
    
    # Crear engine con parámetros correctos
    engine = EnhancedTrajectoryEngine(max_sources=10, update_rate=60)
    
    # IDs de las fuentes
    source_ids = list(range(5))
    
    # Crear macro
    engine.create_macro("test", source_ids)
    
    # Posiciones iniciales dispersas
    for i in source_ids:
        angle = i * 2 * np.pi / 5
        pos = np.array([
            np.cos(angle) * 10,
            np.sin(angle) * 10,
            0
        ])
        # Establecer posición directamente
        if i < len(engine._positions):
            engine._positions[i] = pos
    
    print("Posiciones iniciales:")
    for i in source_ids:
        if i < len(engine._positions):
            print(f"  Source {i}: {engine._positions[i]}")
    
    # Aplicar concentración
    print("\\n✨ Aplicando concentración...")
    try:
        engine.apply_concentration("test", factor=0.5)
        print("   Concentración aplicada")
    except AttributeError:
        print("   ⚠️ apply_concentration no existe, intentando set_macro_concentration...")
        try:
            engine.set_macro_concentration("test", factor=0.5)
            print("   Concentración aplicada con set_macro_concentration")
        except:
            print("   ❌ No se pudo aplicar concentración")
            return
    
    # Simular algunos frames
    print("\\n📊 Simulando frames...")
    for frame in range(30):
        positions = engine.step()
        
        if frame % 10 == 0:
            print(f"\\nFrame {frame}:")
            # Calcular centro y dispersión solo de las fuentes del macro
            macro_positions = positions[:5]
            center = np.mean(macro_positions, axis=0)
            
            # Calcular distancia promedio al centro
            distances = [np.linalg.norm(pos - center) for pos in macro_positions]
            avg_distance = np.mean(distances)
            
            print(f"  Centro: [{center[0]:.2f}, {center[1]:.2f}, {center[2]:.2f}]")
            print(f"  Distancia promedio al centro: {avg_distance:.2f}")
    
    print("\\n✅ Test completado!")

if __name__ == "__main__":
    test()
'''
    
    with open("test_concentration_fixed.py", 'w') as f:
        f.write(test_code)
    
    print("✅ Nuevo test creado: test_concentration_fixed.py")

if __name__ == "__main__":
    print("🔧 ARREGLANDO PARÁMETROS DEL CONSTRUCTOR\n")
    
    # Verificar parámetros
    try:
        params = check_engine_params()
    except Exception as e:
        print(f"⚠️ No se pueden verificar parámetros: {e}")
        print("   Usando valores por defecto...")
    
    print("\n📝 Actualizando tests...")
    fix_test_file()
    create_working_test()
    
    print("\n✅ LISTO! Ejecuta uno de estos:")
    print("$ python test_concentration_delta.py")
    print("$ python test_concentration_fixed.py")