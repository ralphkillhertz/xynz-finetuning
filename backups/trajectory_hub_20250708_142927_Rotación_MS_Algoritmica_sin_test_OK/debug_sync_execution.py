# === debug_sync_execution.py ===
# 🔍 Debug: Ver si la sincronización se ejecuta realmente
# ⚡ Rastrear línea por línea

import numpy as np
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from trajectory_hub import EnhancedTrajectoryEngine

def debug_sync_execution():
    """Debug detallado de la ejecución de sincronización"""
    
    print("🔍 DEBUG: Ejecución de sincronización")
    print("=" * 60)
    
    # Setup mínimo
    engine = EnhancedTrajectoryEngine(max_sources=2, fps=60)
    engine.create_source(0, "test_0")
    engine._positions[0] = np.array([10.0, 0.0, 0.0])
    
    macro_name = engine.create_macro("test", source_count=1)
    engine.set_macro_rotation(macro_name, center=[0,0,0], speed_x=0, speed_y=2, speed_z=0)
    
    print("✅ Setup completo")
    
    # Verificar estado inicial
    motion = engine.motion_states[0]
    print(f"\n📊 Estado inicial:")
    print(f"  motion.state.position: {motion.state.position}")
    print(f"  engine._positions[0]: {engine._positions[0]}")
    print(f"  ¿Son iguales?: {np.array_equal(motion.state.position, engine._positions[0])}")
    
    # Interceptar el método update para debug detallado
    original_update = engine.update
    
    def debug_update():
        print("\n🔧 INICIO engine.update()")
        
        # Simular el código exacto del update
        print("\n>>> Simulando código de update:")
        
        # Este es el loop de procesamiento de deltas
        for source_id, motion in engine.motion_states.items():
            print(f"\n  Processing source_id {source_id}:")
            print(f"    motion tipo: {type(motion).__name__}")
            print(f"    hasattr(motion, 'state'): {hasattr(motion, 'state')}")
            
            # CRÍTICO: Sincronizar state.position ANTES de calcular deltas
            if hasattr(motion, 'state'):
                print(f"    ✅ Entrando al if hasattr(motion, 'state')")
                print(f"    state.position ANTES sync: {motion.state.position}")
                print(f"    _positions[{source_id}] actual: {engine._positions[source_id]}")
                
                # SINCRONIZACIÓN
                motion.state.position = engine._positions[source_id].copy()
                
                print(f"    state.position DESPUÉS sync: {motion.state.position}")
                print(f"    ✅ Sincronización ejecutada")
            else:
                print(f"    ❌ NO tiene 'state'")
            
            if hasattr(motion, 'update_with_deltas'):
                print(f"\n    Llamando update_with_deltas...")
                print(f"    state.position al llamar: {motion.state.position}")
                
                deltas = motion.update_with_deltas(engine._time, engine.dt)
                print(f"    Deltas retornados: {len(deltas)}")
                
                for i, delta in enumerate(deltas):
                    if hasattr(delta, 'position') and delta.position is not None:
                        print(f"      Delta {i}: {delta.position}")
                        # Aplicar delta
                        engine._positions[source_id] = engine._positions[source_id] + delta.position
                        print(f"      Nueva posición: {engine._positions[source_id]}")
        
        # NO llamar al update original para evitar doble procesamiento
        print("\n>>> FIN simulación")
        
        # Actualizar tiempo
        engine._time += engine.dt
        engine._frame_count += 1
    
    # Reemplazar temporalmente
    engine.update = debug_update
    
    # Ejecutar UN frame
    print("\n" + "="*60)
    print("⏱️ Ejecutando UN frame con debug detallado...")
    engine.update()
    
    # Verificar resultado
    print("\n📊 RESULTADO FINAL:")
    print(f"  motion.state.position: {motion.state.position}")
    print(f"  engine._positions[0]: {engine._positions[0]}")
    print(f"  Distancia movida: {np.linalg.norm(engine._positions[0] - [10.0, 0.0, 0.0]):.6f}")

if __name__ == "__main__":
    debug_sync_execution()