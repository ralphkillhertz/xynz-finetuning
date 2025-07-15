# === diagnose_rotation_final.py ===
# 🔍 Diagnóstico definitivo del problema de rotación
# ⚡ Identifica exactamente por qué no funciona
# 🎯 Impacto: CRÍTICO

import numpy as np
import math

def diagnose_rotation_issue():
    """Diagnóstico completo del sistema de rotación"""
    print("🔍 DIAGNÓSTICO DEFINITIVO: Sistema de Rotación Manual")
    print("="*60)
    
    from trajectory_hub.core import EnhancedTrajectoryEngine
    
    # Crear engine
    engine = EnhancedTrajectoryEngine(max_sources=50, fps=60, enable_modulator=False)
    
    # Crear macro y verificar nombre
    print("\n1️⃣ Creando macro...")
    macro_name = engine.create_macro("test_rotation", source_count=4, formation="square")
    print(f"   Macro creado: '{macro_name}'")
    print(f"   Macros disponibles: {list(engine._macros.keys())}")
    
    # Obtener el macro
    macro = engine._macros[macro_name]
    source_ids_list = list(macro.source_ids)
    
    # Establecer posiciones
    positions = [[3,0,0], [0,3,0], [-3,0,0], [0,-3,0]]
    for i, (sid, pos) in enumerate(zip(source_ids_list, positions)):
        engine._positions[sid] = np.array(pos)
        if sid in engine.motion_states:
            engine.motion_states[sid].position = list(pos)
    
    print("\n2️⃣ Configurando rotación manual...")
    # Usar el nombre correcto del macro
    engine.set_manual_macro_rotation(macro_name, yaw=math.pi/2, interpolation_speed=1.0)
    
    # Verificar que se configuró
    print("\n3️⃣ Verificando componentes activos...")
    for sid in source_ids_list[:1]:  # Solo verificar la primera
        state = engine.motion_states[sid]
        print(f"   Fuente {sid}:")
        print(f"      active_components: {list(state.active_components.keys())}")
        
        if 'manual_macro_rotation' in state.active_components:
            rot = state.active_components['manual_macro_rotation']
            print(f"      ✅ ManualMacroRotation presente")
            print(f"         enabled: {rot.enabled}")
            print(f"         target_yaw: {np.degrees(rot.target_yaw):.1f}°")
            print(f"         interpolation_speed: {rot.interpolation_speed}")
        else:
            print(f"      ❌ NO hay ManualMacroRotation")
    
    # Test manual del algoritmo
    print("\n4️⃣ Test manual del calculate_delta...")
    if source_ids_list and 'manual_macro_rotation' in engine.motion_states[source_ids_list[0]].active_components:
        state = engine.motion_states[source_ids_list[0]]
        rot = state.active_components['manual_macro_rotation']
        
        # Calcular delta manualmente
        delta = rot.calculate_delta(state, 0.0, 1/60.0)
        if delta:
            print(f"   Delta calculado: {delta.position}")
        else:
            print("   ❌ calculate_delta retornó None")
    
    # Ejecutar un paso de update
    print("\n5️⃣ Ejecutando engine.update()...")
    pos_before = engine._positions[source_ids_list[0]].copy()
    engine.update()
    pos_after = engine._positions[source_ids_list[0]]
    
    print(f"   Posición antes: {pos_before}")
    print(f"   Posición después: {pos_after}")
    print(f"   Cambio: {pos_after - pos_before}")
    
    if np.allclose(pos_before, pos_after):
        print("   ❌ La posición NO cambió")
        
        # Verificar el flujo de update
        print("\n6️⃣ Verificando flujo de update...")
        
        # Verificar si motion.update se ejecuta
        state = engine.motion_states[source_ids_list[0]]
        if hasattr(state, 'update'):
            print("   ❌ MotionState no debería tener método update")
        
        # Verificar si hay un SourceMotion
        print(f"   motion_states[{source_ids_list[0]}] tipo: {type(state)}")
        
        # El problema puede estar en cómo engine.update() procesa los componentes
        print("\n   ⚠️ PROBLEMA: engine.update() no está procesando ManualMacroRotation")
        print("   Posibles causas:")
        print("   - update() no llama a motion.update() para cada SourceMotion")
        print("   - ManualMacroRotation no está en active_components")
        print("   - El sistema de deltas no se está aplicando")
    else:
        print("   ✅ La posición cambió")

if __name__ == "__main__":
    diagnose_rotation_issue()