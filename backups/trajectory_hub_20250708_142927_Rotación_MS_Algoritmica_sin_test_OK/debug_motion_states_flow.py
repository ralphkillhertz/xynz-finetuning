# === debug_motion_states_flow.py ===
# 🔍 Debug: Rastrear exactamente qué pasa con motion_states
# ⚡ Para encontrar el problema real

import numpy as np
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from trajectory_hub import EnhancedTrajectoryEngine

def debug_motion_states():
    """Debug completo del flujo de motion_states"""
    
    print("🔍 DEBUG PROFUNDO: motion_states y deltas")
    print("=" * 60)
    
    # Crear setup simple
    engine = EnhancedTrajectoryEngine(max_sources=5, fps=60)
    
    # Crear UNA sola fuente
    sid = engine.create_source(0, "test_0")
    engine._positions[0] = np.array([10.0, 0.0, 0.0])
    print(f"✅ Fuente creada: {sid}")
    
    # Verificar motion_states
    print(f"\n📊 motion_states contiene: {list(engine.motion_states.keys())}")
    print(f"   _positions contiene: {list(range(len(engine._positions)))[:5]}")
    
    # Crear macro
    macro_name = engine.create_macro("test", source_count=1)
    print(f"\n✅ Macro creado: {macro_name}")
    
    # Verificar macro
    if macro_name in engine._macros:
        macro = engine._macros[macro_name]
        print(f"   source_ids en macro: {list(macro.source_ids)}")
    
    # Aplicar rotación
    engine.set_macro_rotation(macro_name, center=[0,0,0], speed_x=0, speed_y=2, speed_z=0)
    print("\n✅ Rotación aplicada")
    
    # DEBUG: Ver qué tiene motion_states[0]
    if 0 in engine.motion_states:
        motion = engine.motion_states[0]
        print(f"\n📋 motion_states[0]:")
        print(f"   tipo: {type(motion).__name__}")
        print(f"   tiene state: {hasattr(motion, 'state')}")
        print(f"   tiene active_components: {hasattr(motion, 'active_components')}")
        
        if hasattr(motion, 'active_components'):
            print(f"   active_components: {list(motion.active_components.keys())}")
            
            if 'macro_rotation' in motion.active_components:
                rot = motion.active_components['macro_rotation']
                print(f"\n   macro_rotation:")
                print(f"     enabled: {rot.enabled}")
                print(f"     speed_y: {rot.speed_y}")
                print(f"     tiene calculate_delta: {hasattr(rot, 'calculate_delta')}")
    
    # INTERCEPTAR update() para ver qué pasa
    print("\n🔧 Interceptando engine.update()...")
    
    original_update = engine.update
    
    def debug_update():
        print("\n>>> INICIO engine.update()")
        
        # Ver estado antes
        print(f"    _time: {engine._time}")
        print(f"    motion_states keys: {list(engine.motion_states.keys())}")
        
        # Verificar si el loop se ejecuta
        count = 0
        for source_id, motion in engine.motion_states.items():
            count += 1
            print(f"\n    Procesando source_id {source_id}:")
            print(f"      motion tipo: {type(motion).__name__}")
            
            # Ver si tiene state
            if hasattr(motion, 'state'):
                print(f"      state.position ANTES: {motion.state.position}")
                print(f"      _positions[{source_id}]: {engine._positions[source_id]}")
            
            # Ver si tiene update_with_deltas
            if hasattr(motion, 'update_with_deltas'):
                print(f"      tiene update_with_deltas: ✅")
                
                # Llamar manualmente para debug
                try:
                    deltas = motion.update_with_deltas(engine._time, 1/60.0)
                    print(f"      deltas retornados: {len(deltas)}")
                    for delta in deltas:
                        if hasattr(delta, 'position'):
                            print(f"        delta.position: {delta.position}")
                except Exception as e:
                    print(f"      ERROR en update_with_deltas: {e}")
        
        print(f"\n    Total fuentes procesadas: {count}")
        
        # Llamar al original
        result = original_update()
        
        print("\n>>> FIN engine.update()")
        print(f"    Posición final [0]: {engine._positions[0]}")
        
        return result
    
    # Reemplazar temporalmente
    engine.update = debug_update
    
    # Ejecutar UN frame
    print("\n" + "="*60)
    print("⏱️ Ejecutando UN frame con debug...")
    engine.update()
    
    # Verificar resultado
    dist = np.linalg.norm(engine._positions[0] - [10.0, 0.0, 0.0])
    print(f"\n📊 RESULTADO: Distancia movida = {dist:.6f}")

if __name__ == "__main__":
    debug_motion_states()