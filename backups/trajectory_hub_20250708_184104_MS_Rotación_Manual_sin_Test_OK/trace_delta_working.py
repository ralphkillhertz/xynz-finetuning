# === trace_delta_working.py ===
# 🔍 Rastrear transformación de deltas - VERSIÓN FUNCIONAL
# ⚡ Debug profundo del flujo de rotación

import sys
import os
import numpy as np
import math
import time

# Añadir la ruta del proyecto al PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def trace_delta_flow():
    """Rastrea el flujo completo del delta desde calculate_delta hasta las posiciones"""
    print("🔍 RASTREANDO FLUJO DE DELTAS")
    print("=" * 60)
    
    from trajectory_hub.core import EnhancedTrajectoryEngine
    
    # Crear engine simple
    print("\n1️⃣ Creando engine...")
    engine = EnhancedTrajectoryEngine(
        max_sources=50,
        fps=60,
        enable_modulator=False
    )
    
    # NO crear fuentes antes - create_macro las crea automáticamente
    print("\n2️⃣ Creando macro directamente (crea las fuentes)...")
    macro_name = "test_macro"
    
    # API correcta: create_macro(name, source_count, formation)
    engine.create_macro(macro_name, 4, formation="square")
    
    # Verificar que se creó
    if macro_name not in engine._macros:
        print("❌ Error: macro no se creó")
        print(f"   Macros disponibles: {list(engine._macros.keys())}")
        return
    
    macro = engine._macros[macro_name]
    print(f"✅ Macro creado con {len(macro.source_ids)} fuentes")
    print(f"   IDs: {macro.source_ids}")
    
    # Establecer posiciones específicas para el test
    print("\n3️⃣ Estableciendo posiciones de test...")
    positions = [[3, 0, 0], [0, 3, 0], [-3, 0, 0], [0, -3, 0]]
    
    for i, (sid, pos) in enumerate(zip(macro.source_ids, positions)):
        engine._positions[sid] = np.array(pos, dtype=np.float32)
        print(f"   Fuente {sid}: {pos}")
    
    # Configurar rotación manual
    print("\n4️⃣ Configurando rotación manual...")
    engine.set_manual_macro_rotation(
        macro_name,
        yaw=math.pi/2,    # 90 grados
        pitch=0,
        roll=0,
        interpolation_speed=0.1
    )
    
    # Buscar componente de rotación
    print("\n5️⃣ Verificando componente de rotación...")
    component = None
    test_motion = None
    
    for sid in macro.source_ids:
        if sid in engine.motion_states:
            motion = engine.motion_states[sid]
            if hasattr(motion, 'active_components') and 'manual_macro_rotation' in motion.active_components:
                component = motion.active_components['manual_macro_rotation']
                test_motion = motion
                break
    
    if not component:
        print("❌ No se encontró componente de rotación")
        # Debug
        if macro.source_ids and macro.source_ids[0] in engine.motion_states:
            motion = engine.motion_states[macro.source_ids[0]]
            print(f"   Tipo de motion: {type(motion).__name__}")
            if hasattr(motion, 'active_components'):
                print(f"   Componentes activos: {list(motion.active_components.keys())}")
            else:
                print("   ❌ Motion no tiene active_components")
        return
    
    print(f"✅ Componente encontrado: {type(component).__name__}")
    print(f"   Enabled: {component.enabled}")
    print(f"   Target yaw: {component.target_yaw:.3f} rad ({math.degrees(component.target_yaw):.1f}°)")
    print(f"   Interpolation speed: {component.interpolation_speed}")
    
    # Test directo de calculate_delta
    print("\n6️⃣ TEST DIRECTO de calculate_delta:")
    print("-" * 40)
    
    test_state = engine.motion_states[macro.source_ids[0]]
    print(f"   Posición inicial del estado: {test_state.position}")
    
    # Sincronizar el estado con la posición real
    test_state.position = engine._positions[macro.source_ids[0]].copy()
    print(f"   Posición sincronizada: {test_state.position}")
    
    # Llamar calculate_delta
    delta = component.calculate_delta(test_state, 0.0, 0.016)
    
    if delta and delta.position is not None:
        print(f"   ✅ Delta calculado: {delta.position}")
        print(f"      Magnitud: {np.linalg.norm(delta.position):.6f}")
    else:
        print("   ❌ calculate_delta retornó None o sin posición")
    
    # Guardar posiciones antes
    print("\n7️⃣ POSICIONES ANTES del update:")
    positions_before = {}
    for sid in macro.source_ids:
        positions_before[sid] = engine._positions[sid].copy()
        print(f"   Fuente {sid}: {positions_before[sid]}")
    
    # Ejecutar engine.update()
    print("\n8️⃣ Ejecutando engine.update()...")
    
    # Sincronizar estados antes del update
    for sid in macro.source_ids:
        if sid in engine.motion_states:
            engine.motion_states[sid].position = engine._positions[sid].copy()
    
    engine.update()
    
    # Verificar cambios
    print("\n9️⃣ POSICIONES DESPUÉS del update:")
    any_change = False
    for sid in macro.source_ids:
        pos_after = engine._positions[sid]
        diff = pos_after - positions_before[sid]
        magnitude = np.linalg.norm(diff)
        
        if magnitude > 0.0001:
            print(f"   Fuente {sid}: {pos_after} ✅ (cambió {magnitude:.6f})")
            any_change = True
        else:
            print(f"   Fuente {sid}: {pos_after} ❌ (sin cambios)")
    
    # Si no hubo cambios, debug más profundo
    if not any_change:
        print("\n🔍 DEBUG PROFUNDO - No hubo cambios")
        print("-" * 40)
        
        # Verificar si motion.update se llama
        print("Probando actualización manual del motion...")
        
        if test_motion and hasattr(test_motion, 'update'):
            # Actualizar manualmente
            test_motion.update(0.1, 0.016)
            
            # Ver si el componente cambió
            print(f"   Current yaw después de update: {component.current_yaw:.3f}")
            
            # Probar calculate_delta de nuevo
            delta2 = component.calculate_delta(test_state, 0.1, 0.016)
            if delta2:
                print(f"   Delta después de update manual: {delta2.position}")
    
    # Análisis final
    print("\n📊 ANÁLISIS FINAL:")
    print("=" * 60)
    
    if delta and np.any(delta.position != 0):
        print("✅ calculate_delta funciona correctamente")
    else:
        print("❌ calculate_delta NO genera deltas válidos")
    
    if any_change:
        print("✅ engine.update() aplica los cambios")
    else:
        print("❌ engine.update() NO aplica los deltas")
        print("\n   Posible causa: motion.update() no se está llamando")
        print("   o los deltas no se están procesando en engine.update()")

if __name__ == "__main__":
    trace_delta_flow()