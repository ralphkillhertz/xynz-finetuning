#!/usr/bin/env python3
"""
🔍 Diagnóstico: Sistema de Deltas y Concentración
⚡ Objetivo: Identificar por qué no se suman los componentes
"""

import numpy as np
from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
from trajectory_hub.motion.source_motion import SourceMotion
import time

def test_delta_system():
    """Verificar si el sistema de deltas está funcionando"""
    print("🔍 DIAGNÓSTICO DEL SISTEMA DE DELTAS\n")
    
    # Crear engine
    engine = EnhancedTrajectoryEngine()
    
    # Crear macro de prueba
    print("1️⃣ Creando macro de prueba...")
    macro_id = engine.create_macro(
        name="test",
        num_sources=3,
        formation="line",
        spacing=2.0
    )
    print(f"   ✓ Macro creado: {macro_id}")
    
    # Obtener primera fuente
    source_ids = list(engine.macros[macro_id].source_ids)
    test_source_id = source_ids[0]
    test_source = engine.sources[test_source_id]
    
    print(f"\n2️⃣ Analizando fuente: {test_source_id}")
    
    # Verificar estructura de SourceMotion
    print("\n📊 Verificando estructura de SourceMotion:")
    motion = test_source.motion
    
    # Verificar si tiene método update correcto
    if hasattr(motion, 'update'):
        # Leer el código del método update
        import inspect
        update_code = inspect.getsource(motion.update)
        
        print("📝 Método update encontrado")
        
        # Buscar palabras clave
        if "delta" in update_code.lower():
            print("   ✅ Sistema de deltas detectado")
        else:
            print("   ❌ NO se detecta sistema de deltas")
            
        if "_combine_components" in update_code:
            print("   ✅ Método _combine_components presente")
        else:
            print("   ❌ NO se detecta _combine_components")
    
    # Test 1: Concentración sola
    print("\n3️⃣ TEST CONCENTRACIÓN:")
    initial_pos = test_source.get_position().copy()
    print(f"   Posición inicial: {initial_pos}")
    
    # Aplicar concentración
    engine.set_concentration(macro_id, 0.2, animate=False)
    engine.update(0.1)
    
    conc_pos = test_source.get_position().copy()
    print(f"   Posición con concentración: {conc_pos}")
    
    if np.allclose(initial_pos, conc_pos):
        print("   ❌ La concentración NO está modificando la posición")
    else:
        print("   ✅ La concentración SÍ modifica la posición")
        print(f"   Δ = {conc_pos - initial_pos}")
    
    # Test 2: Rotación MS sola
    print("\n4️⃣ TEST ROTACIÓN MS:")
    # Reset concentración
    engine.set_concentration(macro_id, 1.0, animate=False)
    engine.update(0.1)
    
    initial_rot = test_source.get_position().copy()
    
    # Aplicar rotación
    engine.set_algorithmic_rotation(macro_id, "circular", speed=10.0, amplitude=1.0)
    
    # Actualizar varias veces
    for _ in range(5):
        engine.update(0.1)
    
    rot_pos = test_source.get_position().copy()
    print(f"   Posición inicial: {initial_rot}")
    print(f"   Posición con rotación: {rot_pos}")
    
    if np.allclose(initial_rot, rot_pos):
        print("   ❌ La rotación NO está modificando la posición")
    else:
        print("   ✅ La rotación SÍ modifica la posición")
    
    # Test 3: IS + Rotación MS
    print("\n5️⃣ TEST COMBINACIÓN IS + ROTACIÓN MS:")
    
    # Aplicar trayectoria individual
    engine.set_individual_trajectory(test_source_id, "circle", motion_mode="constant")
    
    # Capturar posiciones durante varios frames
    positions = []
    for i in range(10):
        engine.update(0.1)
        pos = test_source.get_position().copy()
        positions.append(pos)
    
    # Analizar movimiento
    print(f"   Primera posición: {positions[0]}")
    print(f"   Última posición: {positions[-1]}")
    
    # Verificar si hay movimiento
    all_same = all(np.allclose(positions[0], p) for p in positions)
    
    if all_same:
        print("   ❌ NO hay movimiento combinado")
    else:
        print("   ✅ Hay movimiento")
        
        # Analizar tipo de movimiento
        # Si solo IS: movimiento circular simple
        # Si IS + Rotación: movimiento más complejo
        
        # Calcular varianza de las distancias entre puntos consecutivos
        distances = [np.linalg.norm(positions[i+1] - positions[i]) for i in range(len(positions)-1)]
        variance = np.var(distances)
        
        if variance < 0.0001:
            print("   📊 Movimiento uniforme (probablemente solo IS)")
        else:
            print("   📊 Movimiento variable (posible combinación)")
    
    # Verificar directamente los componentes
    print("\n6️⃣ INSPECCIÓN DIRECTA DE COMPONENTES:")
    
    # Acceder a motion
    motion = test_source.motion
    
    # Verificar componentes activos
    if hasattr(motion, 'trajectory_offset'):
        print(f"   trajectory_offset: {motion.trajectory_offset}")
    
    if hasattr(motion, 'concentration_offset'):
        print(f"   concentration_offset: {motion.concentration_offset}")
        
    if hasattr(motion, 'macro_rotation_offset'):
        print(f"   macro_rotation_offset: {motion.macro_rotation_offset}")
    
    # Verificar si _combine_components existe
    if hasattr(motion, '_combine_components'):
        print("\n   🔧 Ejecutando _combine_components manualmente...")
        result = motion._combine_components()
        print(f"   Resultado: {result}")
    else:
        print("\n   ❌ NO existe _combine_components")
    
    print("\n" + "="*50)
    print("📋 RESUMEN DEL DIAGNÓSTICO:")
    print("="*50)
    
    return engine

if __name__ == "__main__":
    engine = test_delta_system()
    
    print("\n💡 RECOMENDACIONES:")
    print("1. Si la concentración no modifica posición → Revisar spatial_concentration.py")
    print("2. Si no hay sistema de deltas → Re-aplicar arquitectura de deltas")
    print("3. Si los componentes no se combinan → Verificar _combine_components")