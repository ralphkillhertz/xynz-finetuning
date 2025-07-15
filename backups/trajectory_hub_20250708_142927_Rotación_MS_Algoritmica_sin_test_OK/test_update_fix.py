# === test_update_fix.py ===
# Test para verificar que engine.update() actualiza las trayectorias

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trajectory_hub import EnhancedTrajectoryEngine
import time

def test_update_motion():
    """Verifica que el update actualice las posiciones"""
    print("\n🧪 TEST: Verificando engine.update() con trayectorias")
    print("=" * 60)
    
    # Crear engine
    engine = EnhancedTrajectoryEngine(max_sources=10, fps=60)
    print("✅ Engine creado")
    
    # Crear un macro
    engine.create_macro("test", 5)
    print("✅ Macro creado con 5 fuentes")
    
    # Configurar trayectorias individuales
    config = {
        'mode': 1,  # Todas iguales
        'shape': 'circle',
        'movement_mode': 'fix',
        'speed': 1.0
    }
    engine.configure_individual_trajectories("test", config)
    print("✅ Trayectorias configuradas")
    
    # Obtener posiciones iniciales
    initial_positions = []
    for sid in engine.macros["test"].source_ids:
        initial_positions.append(engine._positions[sid].copy())
    
    print(f"\n📍 Posiciones iniciales:")
    for i, pos in enumerate(initial_positions):
        print(f"   Fuente {i}: {pos}")
    
    # Ejecutar varios updates
    print("\n🔄 Ejecutando 10 updates...")
    for i in range(10):
        engine.update(0.1)  # 100ms por update
        time.sleep(0.01)
    
    # Verificar que las posiciones cambiaron
    print("\n📍 Posiciones después de updates:")
    positions_moved = False
    for i, sid in enumerate(engine.macros["test"].source_ids):
        current_pos = engine._positions[sid]
        initial_pos = initial_positions[i]
        
        # Calcular diferencia
        diff = sum(abs(current_pos[j] - initial_pos[j]) for j in range(3))
        moved = diff > 0.01
        
        print(f"   Fuente {sid}: {current_pos} {'✅ MOVIDA' if moved else '❌ NO MOVIDA'}")
        if moved:
            positions_moved = True
    
    # Verificar motion_states
    print("\n🔍 Verificando motion_states:")
    for sid in engine.macros["test"].source_ids:
        if sid in engine.motion_states:
            motion = engine.motion_states[sid]
            if hasattr(motion, 'state'):
                state = motion.state
                print(f"   Fuente {sid}: fase = {getattr(state, 'position_on_trajectory', 0):.3f}")
    
    if positions_moved:
        print("\n✅ ¡ÉXITO! Las trayectorias se están moviendo correctamente")
    else:
        print("\n❌ ERROR: Las trayectorias NO se están moviendo")
        print("\n🔍 Debugging adicional:")
        # Verificar si hay componentes activos
        for sid in engine.macros["test"].source_ids:
            if sid in engine.motion_states:
                motion = engine.motion_states[sid]
                print(f"\nFuente {sid}:")
                print(f"  - SourceMotion existe: ✅")
                if hasattr(motion, 'active_components'):
                    print(f"  - Componentes activos: {list(motion.active_components.keys())}")
                    for comp_name, comp in motion.active_components.items():
                        if hasattr(comp, 'enabled'):
                            print(f"    - {comp_name}: {'✅ Habilitado' if comp.enabled else '❌ Deshabilitado'}")
    
    return positions_moved

if __name__ == "__main__":
    test_update_motion()
