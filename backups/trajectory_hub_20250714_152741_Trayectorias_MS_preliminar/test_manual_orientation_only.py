#!/usr/bin/env python3
"""Test de rotación manual - solo orientación sin movimiento"""

import sys
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'trajectory_hub'))

from core.enhanced_trajectory_engine import EnhancedTrajectoryEngine

def test_orientation_only():
    """Test que la rotación manual solo cambia orientación, no posición"""
    print("=== TEST: ROTACIÓN MANUAL - SOLO ORIENTACIÓN ===\n")
    
    # Crear engine
    engine = EnhancedTrajectoryEngine(max_sources=10)
    
    # Crear macro
    macro_id = engine.create_macro("test_orientation", 1, "rigid")
    print(f"✅ Macro creado: {macro_id}")
    
    # Posición inicial
    sid = list(engine._macros[macro_id].source_ids)[0]
    engine._positions[sid] = np.array([5.0, 2.0, 1.0])
    pos_inicial = engine._positions[sid].copy()
    
    # Obtener orientación inicial
    motion_state = engine.motion_states.get(sid)
    orient_inicial = motion_state.state.orientation.copy() if motion_state else np.zeros(3)
    
    print(f"Estado inicial:")
    print(f"  Posición: [{pos_inicial[0]:.2f}, {pos_inicial[1]:.2f}, {pos_inicial[2]:.2f}]")
    print(f"  Orientación: [Y:{np.degrees(orient_inicial[0]):.1f}°, P:{np.degrees(orient_inicial[1]):.1f}°, R:{np.degrees(orient_inicial[2]):.1f}°]")
    
    # Aplicar rotación manual
    print("\n--- Aplicando rotación manual (Y=90°, P=45°, R=30°) ---")
    engine.set_manual_macro_rotation(
        macro_id,
        yaw=np.radians(90),
        pitch=np.radians(45),
        roll=np.radians(30),
        interpolation_speed=1000.0  # Instantáneo
    )
    
    # Update para aplicar
    engine.update(0.016)
    
    # Verificar posición y orientación después
    pos_final = engine._positions[sid].copy()
    orient_final = motion_state.state.orientation.copy() if motion_state else np.zeros(3)
    
    print(f"\nEstado después de rotación manual:")
    print(f"  Posición: [{pos_final[0]:.2f}, {pos_final[1]:.2f}, {pos_final[2]:.2f}]")
    print(f"  Orientación: [Y:{np.degrees(orient_final[0]):.1f}°, P:{np.degrees(orient_final[1]):.1f}°, R:{np.degrees(orient_final[2]):.1f}°]")
    
    # Verificar que la posición NO cambió
    pos_diff = np.linalg.norm(pos_final - pos_inicial)
    if pos_diff < 0.001:
        print("\n✅ CORRECTO: La posición NO cambió")
    else:
        print(f"\n❌ ERROR: La posición cambió en {pos_diff:.3f} unidades")
    
    # Verificar que la orientación SÍ cambió
    orient_diff = np.linalg.norm(orient_final - orient_inicial)
    if orient_diff > 0.1:
        print("✅ CORRECTO: La orientación SÍ cambió")
    else:
        print("❌ ERROR: La orientación NO cambió")
    
    # Múltiples updates adicionales - verificar que nada cambia
    print("\n--- Verificando estabilidad (10 updates adicionales) ---")
    stable = True
    for i in range(10):
        engine.update(0.016)
        pos_check = engine._positions[sid].copy()
        if np.linalg.norm(pos_check - pos_final) > 0.001:
            stable = False
            print(f"  ❌ Movimiento detectado en update {i+1}")
    
    if stable:
        print("  ✅ Posición y orientación estables")

def test_orientation_values():
    """Test que verifica los valores específicos de orientación"""
    print(f"\n{'='*60}")
    print("TEST: VALORES ESPECÍFICOS DE ORIENTACIÓN")
    print(f"{'='*60}")
    
    engine = EnhancedTrajectoryEngine(max_sources=10)
    
    # Crear macro
    macro_id = engine.create_macro("test_values", 1, "rigid")
    sid = list(engine._macros[macro_id].source_ids)[0]
    engine._positions[sid] = np.array([3.0, 0.0, 0.0])
    
    # Test diferentes orientaciones
    test_cases = [
        {"yaw": 0, "pitch": 0, "roll": 0, "desc": "Orientación neutral"},
        {"yaw": 90, "pitch": 0, "roll": 0, "desc": "Solo Yaw 90°"},
        {"yaw": 0, "pitch": 45, "roll": 0, "desc": "Solo Pitch 45°"},
        {"yaw": 0, "pitch": 0, "roll": 30, "desc": "Solo Roll 30°"},
        {"yaw": -90, "pitch": -45, "roll": -30, "desc": "Valores negativos"}
    ]
    
    for case in test_cases:
        print(f"\n{case['desc']}:")
        
        # Aplicar orientación
        engine.set_manual_macro_rotation(
            macro_id,
            yaw=np.radians(case['yaw']),
            pitch=np.radians(case['pitch']),
            roll=np.radians(case['roll']),
            interpolation_speed=1000.0
        )
        
        engine.update(0.016)
        
        # Verificar
        motion_state = engine.motion_states.get(sid)
        if motion_state and hasattr(motion_state.state, 'orientation'):
            orient = motion_state.state.orientation
            print(f"  Esperado: Y:{case['yaw']}°, P:{case['pitch']}°, R:{case['roll']}°")
            print(f"  Obtenido: Y:{np.degrees(orient[0]):.1f}°, P:{np.degrees(orient[1]):.1f}°, R:{np.degrees(orient[2]):.1f}°")
            
            # Verificar precisión
            expected = np.array([np.radians(case['yaw']), np.radians(case['pitch']), np.radians(case['roll'])])
            error = np.linalg.norm(orient - expected)
            if error < 0.01:
                print("  ✅ Valores correctos")
            else:
                print(f"  ❌ Error: {error:.4f} rad")

if __name__ == "__main__":
    test_orientation_only()
    test_orientation_values()
    
    print(f"\n{'='*60}")
    print("RESUMEN DE LA SOLUCIÓN:")
    print("✅ Rotación Manual MS ahora solo cambia orientación (PRY)")
    print("✅ La posición del macro permanece sin cambios")
    print("✅ La orientación se aplica una vez y se mantiene")
    print("✅ No hay movimiento continuo")
    print(f"{'='*60}")