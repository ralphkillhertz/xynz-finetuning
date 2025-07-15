#!/usr/bin/env python3
"""
🔍 Diagnóstico Inteligente con Auto-detección
⚡ No requiere conocer la estructura exacta
"""

import sys
import os
import numpy as np
import time

# Auto-detectar ruta del proyecto
current_dir = os.getcwd()
if 'trajectory_hub' in current_dir:
    # Estamos dentro de trajectory_hub
    parent_dir = os.path.dirname(current_dir)
    sys.path.insert(0, parent_dir)

def diagnostic():
    """Diagnóstico del sistema sin imports directos"""
    print("🔍 DIAGNÓSTICO INTELIGENTE DEL SISTEMA\n")
    
    try:
        # Intentar importar el engine
        print("🔄 Importando engine...")
        from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
        print("✅ EnhancedTrajectoryEngine importado correctamente")
    except Exception as e:
        print(f"❌ Error al importar engine: {e}")
        return
    
    # Crear engine de prueba
    print("🔄 Creando engine sin OSC para diagnóstico...")
    
    # Temporalmente deshabilitar OSC
    import os
    os.environ['DISABLE_OSC'] = '1'
    
    engine = EnhancedTrajectoryEngine()
    
    # Desactivar OSC si está activo
    if hasattr(engine, 'bridge') and engine.bridge:
        try:
            engine.bridge.stop()
            engine.bridge = None
            print("   ℹ️  OSC desactivado para el diagnóstico")
        except:
            pass
    
    print("✅ Engine creado\n")
    
    # Test 1: Crear macro
    print("1️⃣ CREANDO MACRO DE PRUEBA")
    try:
        # Intentar con source_count
        macro_id = engine.create_macro(
            name="diagnostic",
            source_count=5,
            formation="line",
            spacing=2.0
        )
    except TypeError as e:
        # Si falla, mostrar los parámetros esperados
        import inspect
        sig = inspect.signature(engine.create_macro)
        print(f"   ❌ Error: {e}")
        print(f"   📝 Parámetros esperados: {sig}")
        return
    print(f"   ✓ Macro creado: {macro_id}")
    
    # Obtener fuentes
    source_ids = list(engine.macros[macro_id].source_ids)
    test_source_id = source_ids[0]
    test_source = engine.sources[test_source_id]
    print(f"   ✓ Fuente de prueba: {test_source_id}")
    
    # Test 2: Concentración
    print("\n2️⃣ TEST CONCENTRACIÓN")
    initial_positions = []
    for sid in source_ids[:3]:  # Solo las primeras 3
        pos = engine.sources[sid].get_position()
        initial_positions.append(pos.copy())
        print(f"   Fuente {sid[-1]}: {pos}")
    
    print("\n   Aplicando concentración 0.1...")
    engine.set_concentration(macro_id, 0.1, animate=False)
    
    # Forzar actualización múltiple
    for _ in range(5):
        engine.update(0.1)
    
    concentrated_positions = []
    movement_detected = False
    
    for i, sid in enumerate(source_ids[:3]):
        pos = engine.sources[sid].get_position()
        concentrated_positions.append(pos.copy())
        delta = pos - initial_positions[i]
        
        if not np.allclose(delta, [0, 0, 0], atol=0.001):
            movement_detected = True
            print(f"   Fuente {sid[-1]}: {pos} (Δ = {delta})")
        else:
            print(f"   Fuente {sid[-1]}: {pos} (SIN CAMBIO)")
    
    if movement_detected:
        print("   ✅ CONCENTRACIÓN FUNCIONA")
    else:
        print("   ❌ CONCENTRACIÓN NO MODIFICA POSICIONES")
    
    # Test 3: Rotación MS
    print("\n3️⃣ TEST ROTACIÓN ALGORÍTMICA MS")
    
    # Reset concentración
    engine.set_concentration(macro_id, 1.0, animate=False)
    engine.update(0.1)
    
    # Guardar posiciones iniciales
    initial_rot_pos = []
    for sid in source_ids[:3]:
        pos = engine.sources[sid].get_position()
        initial_rot_pos.append(pos.copy())
    
    print("   Aplicando rotación circular...")
    engine.set_algorithmic_rotation(macro_id, "circular", speed=5.0, amplitude=1.0)
    
    # Actualizar varias veces
    rotation_detected = False
    for frame in range(10):
        engine.update(0.1)
    
    for i, sid in enumerate(source_ids[:3]):
        pos = engine.sources[sid].get_position()
        delta = pos - initial_rot_pos[i]
        
        if not np.allclose(delta, [0, 0, 0], atol=0.001):
            rotation_detected = True
            print(f"   Fuente {sid[-1]}: {pos} (Δ = {delta})")
    
    if rotation_detected:
        print("   ✅ ROTACIÓN MS FUNCIONA")
    else:
        print("   ❌ ROTACIÓN MS NO MODIFICA POSICIONES")
    
    # Test 4: Combinación IS + MS
    print("\n4️⃣ TEST COMBINACIÓN IS + ROTACIÓN MS")
    
    # Aplicar trayectoria individual
    print("   Aplicando trayectoria circular IS...")
    engine.set_individual_trajectory(test_source_id, "circle", motion_mode="constant")
    
    # Capturar movimiento durante varios frames
    positions_combined = []
    for frame in range(20):
        engine.update(0.05)
        pos = test_source.get_position()
        positions_combined.append(pos.copy())
    
    # Analizar el patrón de movimiento
    # Si solo IS: las posiciones formarán un círculo simple
    # Si IS + Rotación: patrón más complejo
    
    # Calcular centro del movimiento
    center = np.mean(positions_combined, axis=0)
    
    # Calcular distancias al centro
    distances = [np.linalg.norm(p - center) for p in positions_combined]
    distance_variance = np.var(distances)
    
    print(f"\n   Análisis del movimiento:")
    print(f"   - Centro promedio: {center}")
    print(f"   - Varianza de distancias: {distance_variance:.6f}")
    
    if distance_variance < 0.01:
        print("   📊 Movimiento circular uniforme (solo IS activo)")
        print("   ❌ LA ROTACIÓN MS SE PIERDE AL ACTIVAR IS")
    else:
        print("   📊 Movimiento complejo detectado")
        print("   ✅ IS y ROTACIÓN MS se combinan correctamente")
    
    # Test 5: Inspección directa
    print("\n5️⃣ INSPECCIÓN DE ARQUITECTURA")
    
    # Verificar si motion tiene los atributos esperados
    motion = test_source.motion
    
    attrs_to_check = [
        'trajectory_offset',
        'concentration_offset', 
        'macro_rotation_offset',
        'algorithmic_rotation_offset',
        '_combine_components'
    ]
    
    print("   Verificando atributos en SourceMotion:")
    architecture_ok = True
    
    for attr in attrs_to_check:
        if hasattr(motion, attr):
            print(f"   ✅ {attr} presente")
            if "offset" in attr:
                value = getattr(motion, attr)
                if not np.allclose(value, [0, 0, 0]):
                    print(f"      Valor: {value}")
        else:
            print(f"   ❌ {attr} NO ENCONTRADO")
            architecture_ok = False
    
    # Resumen final
    print("\n" + "="*60)
    print("📊 DIAGNÓSTICO FINAL")
    print("="*60)
    
    if not architecture_ok:
        print("❌ PROBLEMA: La arquitectura de deltas NO está implementada")
        print("   → Necesario re-aplicar implement_delta_architecture.py")
    else:
        print("⚠️  PROBLEMA: Los componentes no se están sumando correctamente")
        print("   → Revisar el método _combine_components()")
    
    print("\n💡 SOLUCIÓN RECOMENDADA:")
    print("   Ejecutar: python fix_delta_combination.py")
    
    return engine

if __name__ == "__main__":
    try:
        diagnostic()
    except Exception as e:
        print(f"\n❌ Error durante diagnóstico: {e}")
        print("\n💡 Verifica que estés en el directorio correcto")
        print("   Debe ser: .../trajectory_hub/")