#!/usr/bin/env python3
"""Test completo de rotación con pitch, yaw y roll"""

import sys
import numpy as np
from pathlib import Path

# Agregar el directorio al path
sys.path.insert(0, str(Path(__file__).parent / 'trajectory_hub'))

from core.enhanced_trajectory_engine import EnhancedTrajectoryEngine

def test_rotaciones_completas():
    print("=== TEST DE ROTACIONES PITCH, YAW, ROLL ===\n")
    
    # Crear engine
    engine = EnhancedTrajectoryEngine(max_sources=10)
    
    # Test 1: Rotación Yaw (Y)
    print("1️⃣ TEST YAW (Rotación en Y)")
    macro_yaw = engine.create_macro("test_yaw", 1, behavior="rigid")
    engine._positions[0] = np.array([4.0, 0.0, 0.0])  # Posición inicial
    
    # Forzar centro en origen para test simple
    if 0 in engine.motion_states and 'manual_macro_rotation' in engine.motion_states[0].active_components:
        engine.motion_states[0].active_components['manual_macro_rotation'].center = np.array([0.0, 0.0, 0.0])
    
    print(f"   Inicial: {engine._positions[0]}")
    engine.set_manual_macro_rotation(macro_yaw, yaw=np.radians(90), interpolation_speed=1.0)
    
    # Asegurar centro en origen
    if 0 in engine.motion_states and 'manual_macro_rotation' in engine.motion_states[0].active_components:
        engine.motion_states[0].active_components['manual_macro_rotation'].center = np.array([0.0, 0.0, 0.0])
    
    engine.update(1.0)
    print(f"   Final: {engine._positions[0]}")
    print(f"   Esperado: [0, 0, -4] (punto rota de X+ hacia Z-)\n")
    
    # Test 2: Rotación Pitch (X)
    print("2️⃣ TEST PITCH (Rotación en X)")
    macro_pitch = engine.create_macro("test_pitch", 1, behavior="rigid")
    source_id = list(engine._macros[macro_pitch].source_ids)[0]
    engine._positions[source_id] = np.array([0.0, 4.0, 0.0])  # Posición inicial
    
    print(f"   Inicial: {engine._positions[source_id]}")
    engine.set_manual_macro_rotation(macro_pitch, pitch=np.radians(90), interpolation_speed=1.0)
    engine.update(1.0)
    print(f"   Final: {engine._positions[source_id]}")
    print(f"   Esperado: [0, 0, 4] (punto rota de Y+ hacia Z+)\n")
    
    # Test 3: Rotación Roll (Z)
    print("3️⃣ TEST ROLL (Rotación en Z)")
    macro_roll = engine.create_macro("test_roll", 1, behavior="rigid")
    source_id = list(engine._macros[macro_roll].source_ids)[0]
    engine._positions[source_id] = np.array([4.0, 0.0, 0.0])  # Posición inicial
    
    print(f"   Inicial: {engine._positions[source_id]}")
    engine.set_manual_macro_rotation(macro_roll, roll=np.radians(90), interpolation_speed=1.0)
    engine.update(1.0)
    print(f"   Final: {engine._positions[source_id]}")
    print(f"   Esperado: [0, 4, 0] (punto rota de X+ hacia Y+)\n")
    
    # Test 4: Rotación combinada
    print("4️⃣ TEST COMBINADO (45° en cada eje)")
    macro_combo = engine.create_macro("test_combo", 1, behavior="rigid")
    source_id = list(engine._macros[macro_combo].source_ids)[0]
    engine._positions[source_id] = np.array([4.0, 0.0, 0.0])  # Posición inicial
    
    print(f"   Inicial: {engine._positions[source_id]}")
    engine.set_manual_macro_rotation(
        macro_combo, 
        pitch=np.radians(45),
        yaw=np.radians(45),
        roll=np.radians(45),
        interpolation_speed=1.0
    )
    engine.update(1.0)
    print(f"   Final: {engine._positions[source_id]}")
    print("   (Rotación compleja combinada)")

if __name__ == "__main__":
    test_rotaciones_completas()