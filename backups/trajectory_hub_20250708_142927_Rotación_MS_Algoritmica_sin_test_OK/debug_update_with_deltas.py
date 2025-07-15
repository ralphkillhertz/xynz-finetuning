# === debug_update_with_deltas.py ===
# 🔍 Debug: Ver qué retorna update_with_deltas
# ⚡ Para entender por qué no hay movimiento

import numpy as np
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from trajectory_hub import EnhancedTrajectoryEngine

def debug_deltas():
    """Debug del sistema de deltas"""
    
    print("🔍 DEBUG: Sistema de Deltas")
    print("=" * 60)
    
    # Crear engine
    engine = EnhancedTrajectoryEngine(max_sources=10, fps=60)
    
    # Crear una fuente
    engine.create_source(0, "test_0")
    engine._positions[0] = np.array([10.0, 0.0, 0.0])
    print("✅ Fuente creada en [10, 0, 0]")
    
    # Crear macro
    macro_name = engine.create_macro("test", source_count=1)
    print(f"✅ Macro creado: {macro_name}")
    
    # Aplicar rotación
    engine.set_macro_rotation(macro_name, center=[0,0,0], speed_x=0, speed_y=1, speed_z=0)
    print("✅ Rotación aplicada")
    
    # Debug del motion
    print("\n🔍 Verificando motion_states[0]:")
    motion = engine.motion_states[0]
    print(f"  - Tipo: {type(motion).__name__}")
    print(f"  - tiene update_with_deltas: {hasattr(motion, 'update_with_deltas')}")
    print(f"  - active_components: {list(motion.active_components.keys()) if hasattr(motion, 'active_components') else 'N/A'}")
    
    if hasattr(motion, 'active_components') and 'macro_rotation' in motion.active_components:
        comp = motion.active_components['macro_rotation']
        print(f"\n  macro_rotation:")
        print(f"    - enabled: {comp.enabled}")
        print(f"    - speed_y: {comp.speed_y}")
        print(f"    - tiene calculate_delta: {hasattr(comp, 'calculate_delta')}")
    
    # Llamar update_with_deltas manualmente
    print("\n🔍 Llamando update_with_deltas manualmente:")
    if hasattr(motion, 'update_with_deltas'):
        try:
            # Sincronizar posición
            motion.state.position = engine._positions[0].copy()
            
            # Llamar método
            deltas = motion.update_with_deltas(0.0, 1/60.0)
            print(f"  - Retornó: {type(deltas)}")
            print(f"  - Longitud: {len(deltas) if hasattr(deltas, '__len__') else 'N/A'}")
            
            if deltas:
                for i, delta in enumerate(deltas):
                    print(f"\n  Delta {i}:")
                    print(f"    - Tipo: {type(delta).__name__}")
                    print(f"    - tiene position: {hasattr(delta, 'position')}")
                    if hasattr(delta, 'position'):
                        print(f"    - position: {delta.position}")
                        print(f"    - magnitud: {np.linalg.norm(delta.position) if delta.position is not None else 'None'}")
            else:
                print("  ⚠️ Deltas vacío o None")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    # Verificar el orden de componentes
    print("\n🔍 Verificando orden de procesamiento:")
    if hasattr(motion, 'component_order'):
        print(f"  component_order: {motion.component_order}")
    else:
        print("  ⚠️ No tiene component_order definido")
        
    # Ver si macro_rotation está en el orden
    print("\n💡 Sugerencia:")
    print("  Si macro_rotation no está en component_order,")
    print("  no se procesará en update_with_deltas")

if __name__ == "__main__":
    debug_deltas()