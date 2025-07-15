# === diagnose_component_access.py ===
# 🔍 Diagnóstico: Ver por qué no se encuentra calculate_delta
# ⚡ Debug del acceso a componentes

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from trajectory_hub import EnhancedTrajectoryEngine

def diagnose_components():
    """Diagnosticar acceso a componentes"""
    
    print("🔧 Diagnóstico de acceso a componentes")
    print("=" * 60)
    
    # Crear engine
    engine = EnhancedTrajectoryEngine(n_sources=10, update_rate=60)
    print("✅ Engine creado")
    
    # Crear fuentes
    source_ids = []
    for i in range(4):
        sid = engine.create_source(f"test_{i}")
        source_ids.append(sid)
    print(f"✅ {len(source_ids)} fuentes creadas")
    
    # Crear macro
    macro_name = engine.create_macro("test_macro", source_count=4)
    print(f"✅ Macro creado: {macro_name}")
    
    # Aplicar rotación
    engine.set_macro_rotation(macro_name, center=[0, 0, 0], speed_x=0, speed_y=1, speed_z=0)
    print("✅ Rotación configurada")
    
    # Verificar componentes
    print("\n🔍 Verificando estructura de datos:")
    
    # Ver motion_states
    print(f"\n1. motion_states tiene {len(engine.motion_states)} elementos")
    
    # Ver active_components para cada fuente
    for i, sid in enumerate(source_ids[:2]):  # Solo las primeras 2
        print(f"\n2. Fuente {sid}:")
        
        if sid in engine.motion_states:
            motion = engine.motion_states[sid]
            print(f"   - motion existe: {motion is not None}")
            
            if hasattr(motion, 'active_components'):
                print(f"   - active_components tipo: {type(motion.active_components)}")
                print(f"   - active_components contenido: {motion.active_components}")
                
                # Si es dict
                if isinstance(motion.active_components, dict):
                    for comp_name, comp in motion.active_components.items():
                        print(f"     * {comp_name}: {type(comp).__name__}")
                        if comp:
                            print(f"       - enabled: {getattr(comp, 'enabled', 'N/A')}")
                            print(f"       - tiene calculate_delta: {hasattr(comp, 'calculate_delta')}")
                            if hasattr(comp, 'calculate_delta'):
                                # Probar llamar al método
                                try:
                                    from trajectory_hub.core.motion_components import MotionState
                                    import numpy as np
                                    
                                    test_state = MotionState()
                                    test_state.position = np.array([1.0, 0.0, 0.0])
                                    
                                    delta = comp.calculate_delta(test_state, 0.0, 0.1)
                                    print(f"       - calculate_delta funciona: ✅")
                                    print(f"         Delta: {delta.position if delta and hasattr(delta, 'position') else 'None'}")
                                except Exception as e:
                                    print(f"       - calculate_delta error: {e}")

if __name__ == "__main__":
    diagnose_components()