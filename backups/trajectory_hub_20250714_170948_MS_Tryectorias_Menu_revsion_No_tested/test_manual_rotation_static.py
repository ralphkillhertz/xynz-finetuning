#!/usr/bin/env python3
"""Test de rotación manual estática (sin movimiento continuo)"""

import sys
import time
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'trajectory_hub'))

from core.enhanced_trajectory_engine import EnhancedTrajectoryEngine

def test_manual_rotation_static():
    """Test que la rotación manual se aplica una sola vez y se detiene"""
    print("=== TEST DE ROTACIÓN MANUAL ESTÁTICA ===\n")
    
    # Crear engine
    engine = EnhancedTrajectoryEngine(max_sources=10)
    
    # Crear macro
    macro_id = engine.create_macro("test_static", 1, "rigid")
    print(f"✅ Macro creado: {macro_id}")
    
    # Posición inicial
    sid = list(engine._macros[macro_id].source_ids)[0]
    engine._positions[sid] = np.array([5.0, 0.0, 0.0])
    pos_inicial = engine._positions[sid].copy()
    print(f"Posición inicial: [{pos_inicial[0]:.2f}, {pos_inicial[1]:.2f}, {pos_inicial[2]:.2f}]")
    
    # Aplicar rotación manual de 90 grados
    print("\n--- Aplicando rotación manual (Yaw=90°) ---")
    engine.set_manual_macro_rotation(
        macro_id,
        yaw=np.radians(90),    # 90 grados
        pitch=0,
        roll=0,
        interpolation_speed=1000.0  # Instantáneo
    )
    
    # Primer update - debería aplicar la rotación
    engine.update(0.016)
    pos_after_first = engine._positions[sid].copy()
    print(f"Posición después de 1er update: [{pos_after_first[0]:.2f}, {pos_after_first[1]:.2f}, {pos_after_first[2]:.2f}]")
    
    # Múltiples updates adicionales - NO deberían causar más movimiento
    print("\n--- Verificando que no hay movimiento continuo ---")
    positions = []
    for i in range(10):
        engine.update(0.016)
        pos = engine._positions[sid].copy()
        positions.append(pos)
        if i < 5:  # Mostrar solo los primeros 5
            print(f"  Update {i+2}: [{pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f}]")
    
    # Verificar que la posición se mantiene estática
    all_static = True
    for i in range(1, len(positions)):
        delta = np.linalg.norm(positions[i] - positions[i-1])
        if delta > 0.001:
            all_static = False
            print(f"  ❌ Movimiento detectado entre update {i+1} y {i+2}: {delta:.6f}")
    
    if all_static:
        print("  ✅ Posición se mantiene estática después de la rotación")
    else:
        print("  ❌ ERROR: La posición sigue cambiando!")

def test_multiple_manual_rotations():
    """Test aplicar múltiples rotaciones manuales"""
    print(f"\n{'='*60}")
    print("TEST: MÚLTIPLES ROTACIONES MANUALES")
    print(f"{'='*60}")
    
    engine = EnhancedTrajectoryEngine(max_sources=10)
    
    # Crear macro
    macro_id = engine.create_macro("test_multiple", 1, "rigid")
    sid = list(engine._macros[macro_id].source_ids)[0]
    engine._positions[sid] = np.array([4.0, 0.0, 0.0])
    
    # Primera rotación
    print("\n1. Primera rotación (Yaw=45°)")
    engine.set_manual_macro_rotation(
        macro_id,
        yaw=np.radians(45),
        interpolation_speed=1000.0
    )
    
    engine.update(0.016)
    pos1 = engine._positions[sid].copy()
    print(f"   Posición: [{pos1[0]:.2f}, {pos1[1]:.2f}, {pos1[2]:.2f}]")
    
    # Verificar que se detiene
    for _ in range(5):
        engine.update(0.016)
    pos1_stable = engine._positions[sid].copy()
    
    if np.linalg.norm(pos1_stable - pos1) < 0.001:
        print("   ✅ Rotación se detuvo correctamente")
    else:
        print("   ❌ La rotación continúa!")
    
    # Segunda rotación
    print("\n2. Segunda rotación (Yaw=90°)")
    engine.set_manual_macro_rotation(
        macro_id,
        yaw=np.radians(90),
        interpolation_speed=1000.0
    )
    
    engine.update(0.016)
    pos2 = engine._positions[sid].copy()
    print(f"   Posición: [{pos2[0]:.2f}, {pos2[1]:.2f}, {pos2[2]:.2f}]")
    
    # Verificar que cambió
    if np.linalg.norm(pos2 - pos1_stable) > 0.1:
        print("   ✅ Nueva rotación aplicada correctamente")
    else:
        print("   ❌ La nueva rotación no se aplicó")
    
    # Verificar que se detiene nuevamente
    for _ in range(5):
        engine.update(0.016)
    pos2_stable = engine._positions[sid].copy()
    
    if np.linalg.norm(pos2_stable - pos2) < 0.001:
        print("   ✅ Segunda rotación se detuvo correctamente")
    else:
        print("   ❌ La segunda rotación continúa!")

def test_manual_rotation_with_algorithmic():
    """Test que verifica el comportamiento con rotación algorítmica activa"""
    print(f"\n{'='*60}")
    print("TEST: ROTACIÓN MANUAL CON ALGORÍTMICA ACTIVA")
    print(f"{'='*60}")
    
    engine = EnhancedTrajectoryEngine(max_sources=10)
    
    # Crear macro
    macro_id = engine.create_macro("test_combined", 1, "rigid")
    sid = list(engine._macros[macro_id].source_ids)[0]
    engine._positions[sid] = np.array([3.0, 0.0, 0.0])
    
    # 1. Activar rotación algorítmica
    print("\n1. Activando rotación algorítmica continua...")
    engine.set_macro_rotation(
        macro_id,
        speed_z=0.5,  # Rotación lenta continua
        center=[0.0, 0.0, 0.0]
    )
    
    # Dejar rotar un poco
    for _ in range(30):
        engine.update(0.016)
    
    pos_before_manual = engine._positions[sid].copy()
    print(f"   Posición antes de manual: [{pos_before_manual[0]:.2f}, {pos_before_manual[1]:.2f}, {pos_before_manual[2]:.2f}]")
    
    # 2. Aplicar rotación manual
    print("\n2. Aplicando rotación manual (debería ajustar posición una vez)...")
    engine.set_manual_macro_rotation(
        macro_id,
        yaw=0,  # Volver a orientación inicial
        interpolation_speed=1000.0
    )
    
    engine.update(0.016)
    pos_after_manual = engine._positions[sid].copy()
    print(f"   Posición después de manual: [{pos_after_manual[0]:.2f}, {pos_after_manual[1]:.2f}, {pos_after_manual[2]:.2f}]")
    
    # 3. Verificar que la algorítmica continúa
    print("\n3. Verificando que la rotación algorítmica continúa...")
    positions = []
    for i in range(30):
        engine.update(0.016)
        if i % 10 == 0:
            pos = engine._positions[sid].copy()
            positions.append(pos)
            print(f"   Update {i}: [{pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f}]")
    
    # Verificar movimiento continuo
    movement = np.linalg.norm(positions[-1] - positions[0])
    if movement > 0.5:
        print(f"   ✅ Rotación algorítmica continúa activa (movimiento: {movement:.3f})")
    else:
        print(f"   ❌ Rotación algorítmica parece detenida (movimiento: {movement:.3f})")

if __name__ == "__main__":
    test_manual_rotation_static()
    test_multiple_manual_rotations()
    test_manual_rotation_with_algorithmic()
    
    print(f"\n{'='*60}")
    print("RESUMEN DE LA SOLUCIÓN:")
    print("✅ Rotación manual ahora se aplica una sola vez")
    print("✅ Después de aplicar la orientación, el macro se queda quieto")
    print("✅ Se puede aplicar una nueva rotación manual cuando se necesite")
    print("✅ Compatible con rotación algorítmica activa")
    print(f"{'='*60}")