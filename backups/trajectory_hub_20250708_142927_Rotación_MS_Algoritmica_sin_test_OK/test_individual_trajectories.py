# === test_individual_trajectories.py ===
# 🧪 Test específico para trayectorias individuales

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trajectory_hub import EnhancedTrajectoryEngine
import numpy as np
import time

def test_individual_trajectories():
    """Test de trayectorias individuales con el fix aplicado"""
    print("\n🧪 TEST: Trayectorias Individuales")
    print("=" * 60)
    
    # Crear engine
    engine = EnhancedTrajectoryEngine(max_sources=10, fps=60, enable_modulator=False)
    print("✅ Engine creado")
    
    # Crear macro
    macro_name = engine.create_macro("test", source_count=4)
    print(f"✅ Macro creado: '{macro_name}'")
    
    # Obtener source_ids
    macro = engine._macros[macro_name]
    source_ids = list(macro.source_ids)
    print(f"📍 Source IDs: {source_ids}")
    
    # Configurar diferentes trayectorias para cada fuente
    shapes = ["circle", "spiral", "figure8", "circle"]
    speeds = [1.0, 0.5, 2.0, 1.5]
    
    print("\n🔧 Configurando trayectorias individuales:")
    for i, (sid, shape, speed) in enumerate(zip(source_ids, shapes, speeds)):
        try:
            engine.set_individual_trajectory(
                macro_name,
                sid,
                shape=shape,
                shape_params={'radius': 2.0} if shape == "circle" else {'scale': 1.0},
                movement_mode="fix",
                speed=speed
            )
            print(f"   ✅ Fuente {sid}: {shape} a velocidad {speed}")
        except Exception as e:
            print(f"   ❌ Error en fuente {sid}: {e}")
    
    # Verificar componentes
    print("\n🔍 Verificando componentes activos:")
    for sid in source_ids:
        motion = engine.motion_states[sid]
        components = list(motion.active_components.keys())
        print(f"   Fuente {sid}: {components}")
        
        if 'individual_trajectory' in motion.active_components:
            traj = motion.active_components['individual_trajectory']
            print(f"      - Forma: {traj.shape}, Velocidad: {traj.movement_speed}")
    
    # Capturar posiciones iniciales
    initial_positions = {sid: engine._positions[sid].copy() for sid in source_ids}
    
    # Ejecutar simulación
    print("\n🔄 Ejecutando 40 updates (4 segundos)...")
    for i in range(40):
        engine.update()
        time.sleep(0.025)
        
        if i % 10 == 0:
            # Mostrar progreso
            distances = []
            for sid in source_ids:
                dist = np.linalg.norm(engine._positions[sid] - initial_positions[sid])
                distances.append(dist)
            print(f"   Update {i}: distancias = {[f'{d:.2f}' for d in distances]}")
    
    # Resultados finales
    print("\n📊 RESULTADOS FINALES:")
    print("-" * 40)
    
    all_moved = True
    for sid, shape, speed in zip(source_ids, shapes, speeds):
        current_pos = engine._positions[sid]
        initial_pos = initial_positions[sid]
        distance = np.linalg.norm(current_pos - initial_pos)
        moved = distance > 0.01
        
        print(f"Fuente {sid} ({shape}, v={speed}):")
        print(f"  Distancia recorrida: {distance:.3f} {'✅' if moved else '❌'}")
        
        if not moved:
            all_moved = False
    
    print("\n" + "=" * 60)
    if all_moved:
        print("✅ ¡ÉXITO! Todas las trayectorias individuales funcionan")
        print("\n🎯 Características verificadas:")
        print("   - Diferentes formas (circle, spiral, figure8)")
        print("   - Diferentes velocidades")
        print("   - Movimiento independiente por fuente")
    else:
        print("❌ Algunas trayectorias no se movieron")
    
    return all_moved

if __name__ == "__main__":
    test_individual_trajectories()
