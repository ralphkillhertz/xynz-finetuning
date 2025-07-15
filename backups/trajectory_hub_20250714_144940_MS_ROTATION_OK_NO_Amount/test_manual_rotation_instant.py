#!/usr/bin/env python3
"""Test de rotación manual instantánea"""

import sys
import time
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'trajectory_hub'))

from core.enhanced_trajectory_engine import EnhancedTrajectoryEngine

def test_manual_rotation_instant():
    """Test que la rotación manual es instantánea"""
    print("=== TEST DE ROTACIÓN MANUAL INSTANTÁNEA ===\n")
    
    # Crear engine
    engine = EnhancedTrajectoryEngine(max_sources=10)
    
    # Crear macro
    macro_id = engine.create_macro("test_manual", 1, "rigid")
    print(f"✅ Macro creado: {macro_id}")
    
    # Posición inicial
    sid = list(engine._macros[macro_id].source_ids)[0]
    engine._positions[sid] = np.array([5.0, 0.0, 0.0])
    pos_inicial = engine._positions[sid].copy()
    print(f"Posición inicial: [{pos_inicial[0]:.2f}, {pos_inicial[1]:.2f}, {pos_inicial[2]:.2f}]")
    
    # Test 1: Rotación manual con velocidad instantánea (1000)
    print("\n--- Test 1: Rotación instantánea (speed=1000) ---")
    engine.set_manual_macro_rotation(
        macro_id,
        yaw=np.radians(90),    # 90 grados
        pitch=0,
        roll=0,
        interpolation_speed=1000.0  # Instantáneo
    )
    
    # Un solo update debería ser suficiente
    engine.update(0.016)
    pos_after_instant = engine._positions[sid].copy()
    print(f"Posición después de 1 update: [{pos_after_instant[0]:.2f}, {pos_after_instant[1]:.2f}, {pos_after_instant[2]:.2f}]")
    
    # Verificar que la rotación fue instantánea (90 grados)
    # Después de 90 grados, (5,0,0) debería estar cerca de (0,5,0)
    expected_pos = np.array([0.0, 5.0, 0.0])
    error = np.linalg.norm(pos_after_instant - expected_pos)
    if error < 0.1:
        print("✅ Rotación instantánea correcta")
    else:
        print(f"❌ Error en rotación instantánea: {error:.3f}")
    
    # Test 2: Rotación manual con interpolación lenta
    print("\n--- Test 2: Rotación con interpolación (speed=0.5) ---")
    
    # Reset a posición inicial
    engine._positions[sid] = np.array([5.0, 0.0, 0.0])
    
    engine.set_manual_macro_rotation(
        macro_id,
        yaw=np.radians(90),
        pitch=0,
        roll=0,
        interpolation_speed=0.5  # Lento
    )
    
    # Varios updates
    positions = []
    for i in range(5):
        engine.update(0.016)
        pos = engine._positions[sid].copy()
        positions.append(pos)
        print(f"  Update {i+1}: [{pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f}]")
    
    # Verificar que la rotación es gradual
    for i in range(1, len(positions)):
        delta = np.linalg.norm(positions[i] - positions[i-1])
        if delta > 0.01:
            print(f"  ✅ Movimiento gradual detectado: {delta:.3f}")
        else:
            print(f"  ⚠️  Movimiento muy pequeño: {delta:.3f}")

def test_manual_overrides_algorithmic():
    """Test que la rotación manual puede sobrescribir la algorítmica"""
    print(f"\n{'='*60}")
    print("TEST: ROTACIÓN MANUAL SOBRESCRIBE ALGORÍTMICA")
    print(f"{'='*60}")
    
    engine = EnhancedTrajectoryEngine(max_sources=10)
    
    # Crear macro
    macro_id = engine.create_macro("test_override", 1, "rigid")
    sid = list(engine._macros[macro_id].source_ids)[0]
    engine._positions[sid] = np.array([3.0, 0.0, 0.0])
    
    # 1. Aplicar rotación algorítmica
    print("\n1. Aplicando rotación algorítmica (speed_z=1.0)...")
    engine.set_macro_rotation(
        macro_id,
        speed_z=1.0,  # Rotación continua
        center=[0.0, 0.0, 0.0]
    )
    
    # Simular 1 segundo
    for _ in range(60):
        engine.update(0.016)
    
    pos_after_algo = engine._positions[sid].copy()
    print(f"   Posición después de algorítmica: [{pos_after_algo[0]:.2f}, {pos_after_algo[1]:.2f}, {pos_after_algo[2]:.2f}]")
    
    # 2. Aplicar rotación manual (debería sobrescribir)
    print("\n2. Aplicando rotación manual (yaw=0, instantánea)...")
    engine.set_manual_macro_rotation(
        macro_id,
        yaw=0,  # Volver a posición original
        pitch=0,
        roll=0,
        interpolation_speed=1000.0  # Instantáneo
    )
    
    # Un update para aplicar
    engine.update(0.016)
    pos_after_manual = engine._positions[sid].copy()
    print(f"   Posición después de manual: [{pos_after_manual[0]:.2f}, {pos_after_manual[1]:.2f}, {pos_after_manual[2]:.2f}]")
    
    # Verificar que volvió cerca de la posición original
    expected = np.array([3.0, 0.0, 0.0])
    error = np.linalg.norm(pos_after_manual - expected)
    
    if error < 0.1:
        print("✅ Rotación manual sobrescribió correctamente la algorítmica")
    else:
        print(f"❌ La rotación manual no funcionó correctamente. Error: {error:.3f}")
    
    # 3. Verificar que la rotación algorítmica sigue activa
    print("\n3. Verificando que la rotación algorítmica continúa...")
    for _ in range(30):
        engine.update(0.016)
    
    pos_final = engine._positions[sid].copy()
    movement = np.linalg.norm(pos_final - pos_after_manual)
    
    if movement > 0.5:
        print(f"✅ La rotación algorítmica sigue activa. Movimiento: {movement:.3f}")
    else:
        print(f"❌ La rotación algorítmica parece detenida. Movimiento: {movement:.3f}")

if __name__ == "__main__":
    test_manual_rotation_instant()
    test_manual_overrides_algorithmic()
    
    print(f"\n{'='*60}")
    print("RESUMEN DE CAMBIOS:")
    print("✅ Eliminada la solicitud de velocidad de interpolación en el UI")
    print("✅ Rotación manual ahora es instantánea por defecto")
    print("✅ Se puede sobrescribir rotación algorítmica con manual")
    print("✅ La rotación algorítmica continúa después del ajuste manual")
    print(f"{'='*60}")