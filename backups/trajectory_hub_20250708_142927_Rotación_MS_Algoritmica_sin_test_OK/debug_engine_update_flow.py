# === debug_engine_update_flow.py ===
# 🔍 Debug: Rastrear el flujo completo de engine.update()
# ⚡ Para encontrar dónde se pierde el movimiento

import numpy as np
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from trajectory_hub import EnhancedTrajectoryEngine

def debug_update_flow():
    """Debug completo del flujo de update"""
    
    print("🔍 DEBUG COMPLETO: Flujo de engine.update()")
    print("=" * 60)
    
    # Crear setup mínimo
    engine = EnhancedTrajectoryEngine(max_sources=2, fps=60)
    engine.create_source(0, "test_0")
    engine._positions[0] = np.array([10.0, 0.0, 0.0])
    
    macro_name = engine.create_macro("test", source_count=1)
    engine.set_macro_rotation(macro_name, center=[0,0,0], speed_x=0, speed_y=1, speed_z=0)
    
    print("✅ Setup completo")
    
    # Verificar estado inicial
    print("\n📍 Estado inicial:")
    print(f"  Posición: {engine._positions[0]}")
    
    # Interceptar el método update para debug
    original_update = engine.update
    update_called = [False]
    
    def debug_update():
        update_called[0] = True
        print("\n🔧 engine.update() llamado")
        
        # Ver motion_states
        print(f"  motion_states: {list(engine.motion_states.keys())}")
        
        # Debug del procesamiento de deltas
        for source_id, motion in engine.motion_states.items():
            print(f"\n  Procesando fuente {source_id}:")
            
            # Ver estado antes
            pos_before = engine._positions[source_id].copy()
            print(f"    Posición antes: {pos_before}")
            
            # Sincronizar
            motion.state.position = engine._positions[source_id].copy()
            
            # Llamar update_with_deltas
            if hasattr(motion, 'update_with_deltas'):
                deltas = motion.update_with_deltas(engine._time, 1/60.0)
                print(f"    Deltas retornados: {len(deltas)}")
                
                for i, delta in enumerate(deltas):
                    if hasattr(delta, 'position') and delta.position is not None:
                        print(f"      Delta {i}: {delta.position} (mag: {np.linalg.norm(delta.position):.6f})")
                        # Aplicar manualmente
                        engine._positions[source_id] = engine._positions[source_id] + delta.position
                        print(f"      Nueva posición: {engine._positions[source_id]}")
        
        # Llamar al update original SIN aplicar deltas otra vez
        # para ver si sobrescribe
        print("\n  Llamando update original...")
        result = original_update()
        
        # Ver posición después
        print(f"\n  Posición después del update original: {engine._positions[0]}")
        
        return result
    
    # Reemplazar temporalmente
    engine.update = debug_update
    
    # Ejecutar un frame
    print("\n⏱️ Ejecutando UN frame...")
    engine.update()
    
    # Resultado
    print("\n📊 RESULTADO:")
    print(f"  Posición final: {engine._positions[0]}")
    print(f"  ¿Se movió?: {not np.array_equal(engine._positions[0], [10.0, 0.0, 0.0])}")
    
    # Buscar el problema en el update original
    print("\n🔍 Analizando engine.update original...")
    
    # Ver si hay algo que resetee las posiciones
    import inspect
    try:
        source = inspect.getsource(original_update)
        lines = source.split('\n')
        
        print("\n📋 Líneas sospechosas en update():")
        for i, line in enumerate(lines):
            if '_positions[' in line and '=' in line and 'self._positions[source_id] + delta.position' not in line:
                print(f"  L{i}: {line.strip()}")
                if 'copy()' in line or 'np.array' in line or 'zeros' in line:
                    print("      ^^^ POSIBLE SOBRESCRITURA")
    except:
        pass

if __name__ == "__main__":
    debug_update_flow()