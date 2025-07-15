# === test_simple_trajectory.py ===
# 🧪 Test simple para verificar que las trayectorias se mueven

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trajectory_hub import EnhancedTrajectoryEngine
import numpy as np
import time

def test_trajectory_movement():
    """Test minimalista de movimiento de trayectorias"""
    print("\n🧪 TEST SIMPLE: Movimiento de trayectorias")
    print("=" * 60)
    
    # Crear engine sin modulador para simplificar
    engine = EnhancedTrajectoryEngine(max_sources=10, fps=60, enable_modulator=False)
    print("✅ Engine creado")
    
    # Crear un macro
    engine.create_macro("test", source_count=3)  # Usar source_count, no lista
    print("✅ Macro creado con 3 fuentes")
    
    # Obtener los IDs reales del macro
    source_ids = list(engine.macros["test"].source_ids)
    print(f"📍 IDs de fuentes: {source_ids}")
    
    # Configurar una trayectoria individual simple para cada fuente
    for i, sid in enumerate(source_ids):
        engine.set_individual_trajectory(
            "test", 
            sid, 
            shape="circle",
            shape_params={'radius': 2.0},
            movement_mode="fix",
            speed=1.0
        )
    print("✅ Trayectorias circulares configuradas")
    
    # Capturar posiciones iniciales
    initial_positions = {}
    for sid in source_ids:
        initial_positions[sid] = engine._positions[sid].copy()
        print(f"   Fuente {sid}: posición inicial = {initial_positions[sid]}")
    
    # Ejecutar 20 updates
    print("\n🔄 Ejecutando 20 updates (2 segundos simulados)...")
    for i in range(20):
        engine.update(0.1)  # 100ms por update
        if i % 5 == 0:
            print(f"   Update {i+1}/20")
    
    # Verificar posiciones finales
    print("\n📊 RESULTADOS:")
    print("-" * 40)
    
    all_moved = True
    for sid in source_ids:
        current_pos = engine._positions[sid]
        initial_pos = initial_positions[sid]
        
        # Calcular distancia movida
        distance = np.linalg.norm(current_pos - initial_pos)
        moved = distance > 0.01
        
        print(f"Fuente {sid}:")
        print(f"  Inicial: [{initial_pos[0]:.3f}, {initial_pos[1]:.3f}, {initial_pos[2]:.3f}]")
        print(f"  Final:   [{current_pos[0]:.3f}, {current_pos[1]:.3f}, {current_pos[2]:.3f}]")
        print(f"  Distancia: {distance:.3f} {'✅ MOVIDA' if moved else '❌ NO MOVIDA'}")
        
        if not moved:
            all_moved = False
            
        # Verificar estado del motion
        if sid in engine.motion_states:
            motion = engine.motion_states[sid]
            if hasattr(motion, 'state'):
                phase = getattr(motion.state, 'position_on_trajectory', 0)
                print(f"  Fase en trayectoria: {phase:.3f}")
        print()
    
    # Diagnóstico adicional si no se mueven
    if not all_moved:
        print("\n🔍 DIAGNÓSTICO ADICIONAL:")
        print("-" * 40)
        
        # Verificar que motion_states exista
        print(f"motion_states existe: {'✅' if hasattr(engine, 'motion_states') else '❌'}")
        print(f"Número de motion_states: {len(engine.motion_states)}")
        
        # Verificar componentes activos
        for sid in source_ids[:1]:  # Solo el primero para no saturar
            if sid in engine.motion_states:
                motion = engine.motion_states[sid]
                print(f"\nFuente {sid} - SourceMotion:")
                print(f"  - Tipo: {type(motion).__name__}")
                
                if hasattr(motion, 'active_components'):
                    print(f"  - Componentes activos: {list(motion.active_components.keys())}")
                    
                    # Verificar IndividualTrajectory
                    if 'individual_trajectory' in motion.active_components:
                        traj = motion.active_components['individual_trajectory']
                        print(f"  - IndividualTrajectory:")
                        print(f"    - Habilitada: {getattr(traj, 'enabled', False)}")
                        print(f"    - Forma: {getattr(traj, 'shape', 'N/A')}")
                        print(f"    - Velocidad: {getattr(traj, 'movement_speed', 0)}")
                
                # Llamar update manualmente para debug
                if hasattr(motion, 'update'):
                    print("\n  🧪 Probando update manual...")
                    motion.update(1.0, 0.1)
                    new_phase = getattr(motion.state, 'position_on_trajectory', 0)
                    print(f"    - Fase después de update manual: {new_phase:.3f}")
    
    # Resultado final
    print("\n" + "=" * 60)
    if all_moved:
        print("✅ ¡ÉXITO! Todas las trayectorias se están moviendo")
    else:
        print("❌ ERROR: Las trayectorias NO se están moviendo")
        print("\n💡 Posibles causas:")
        print("   1. engine.update() no llama a motion.update()")
        print("   2. IndividualTrajectory no está habilitada")
        print("   3. movement_speed es 0")
    
    return all_moved

if __name__ == "__main__":
    test_trajectory_movement()