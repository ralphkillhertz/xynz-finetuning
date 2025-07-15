# === verify_macro_rotation_calculate_delta.py ===
# 🔍 Verificar: ¿MacroRotation tiene calculate_delta?
# ⚡ Debug final del problema

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def verify_macro_rotation():
    """Verificar que MacroRotation tenga calculate_delta"""
    
    print("🔍 Verificando MacroRotation.calculate_delta")
    print("=" * 60)
    
    # Importar la clase
    try:
        from trajectory_hub.core.motion_components import MacroRotation
        print("✅ MacroRotation importado correctamente")
    except ImportError as e:
        print(f"❌ Error importando: {e}")
        return
    
    # Crear instancia
    rotation = MacroRotation()
    print(f"✅ Instancia creada: {type(rotation).__name__}")
    
    # Verificar métodos
    print("\n📋 Métodos de MacroRotation:")
    methods = [m for m in dir(rotation) if not m.startswith('_')]
    for method in sorted(methods):
        print(f"  - {method}")
    
    # Verificar calculate_delta específicamente
    print(f"\n🔍 ¿Tiene calculate_delta?: {hasattr(rotation, 'calculate_delta')}")
    
    if hasattr(rotation, 'calculate_delta'):
        print("✅ calculate_delta existe")
        
        # Probar llamarlo
        try:
            from trajectory_hub.core.motion_components import MotionState
            import numpy as np
            
            state = MotionState()
            state.position = np.array([10.0, 0.0, 0.0])
            
            rotation.enabled = True
            rotation.speed_y = 1.0
            rotation.center = np.array([0.0, 0.0, 0.0])
            
            delta = rotation.calculate_delta(state, 0.0, 0.1)
            print(f"\n✅ calculate_delta funciona")
            print(f"   Delta: {delta}")
            if hasattr(delta, 'position'):
                print(f"   Position delta: {delta.position}")
                print(f"   Magnitud: {np.linalg.norm(delta.position):.6f}")
        except Exception as e:
            print(f"\n❌ Error al llamar calculate_delta: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("❌ calculate_delta NO existe")
        print("\n💡 Necesitamos añadir el método calculate_delta a MacroRotation")
        
        # Verificar update_with_deltas en SourceMotion
        print("\n🔍 Verificando SourceMotion.update_with_deltas:")
        try:
            from trajectory_hub.core.motion_components import SourceMotion
            from trajectory_hub import EnhancedTrajectoryEngine
            
            # Crear un engine y fuente para obtener SourceMotion
            engine = EnhancedTrajectoryEngine(max_sources=1, fps=60)
            engine.create_source(0, "test")
            
            if 0 in engine.motion_states:
                motion = engine.motion_states[0]
                print(f"  Tipo: {type(motion).__name__}")
                
                # Ver qué componentes procesa
                if hasattr(motion, 'update_with_deltas'):
                    # Mirar el código
                    import inspect
                    code = inspect.getsource(motion.update_with_deltas)
                    
                    print("\n📋 Código de update_with_deltas:")
                    for line in code.split('\n')[:20]:  # Primeras 20 líneas
                        if 'macro_rotation' in line:
                            print(f"  >>> {line}")
                        else:
                            print(f"      {line}")
                            
        except Exception as e:
            print(f"  Error: {e}")

if __name__ == "__main__":
    verify_macro_rotation()