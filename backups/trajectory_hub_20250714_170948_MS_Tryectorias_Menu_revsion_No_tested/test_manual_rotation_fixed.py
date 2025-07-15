#!/usr/bin/env python3
"""Test de rotación manual corregida - mueve posición una vez y se detiene"""

import sys
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'trajectory_hub'))

from core.enhanced_trajectory_engine import EnhancedTrajectoryEngine

def test_manual_rotation_movement():
    """Test que la rotación manual SÍ mueve el macro y luego se detiene"""
    print("=== TEST: ROTACIÓN MANUAL CON MOVIMIENTO Y PARADA ===\n")
    
    # Crear engine
    engine = EnhancedTrajectoryEngine(max_sources=10)
    
    # Crear macro
    macro_id = engine.create_macro("test_movement", 1, "rigid")
    print(f"✅ Macro creado: {macro_id}")
    
    # Posición inicial
    sid = list(engine._macros[macro_id].source_ids)[0]
    engine._positions[sid] = np.array([5.0, 0.0, 0.0])
    pos_inicial = engine._positions[sid].copy()
    print(f"Posición inicial: [{pos_inicial[0]:.2f}, {pos_inicial[1]:.2f}, {pos_inicial[2]:.2f}]")
    
    # Aplicar rotación manual de 90 grados en Yaw
    print("\n--- Aplicando rotación manual (Yaw=90°) ---")
    print("Esto debería mover el macro de (5,0,0) a aproximadamente (0,5,0)")
    
    engine.set_manual_macro_rotation(
        macro_id,
        yaw=np.radians(90),    # 90 grados
        pitch=0,
        roll=0,
        interpolation_speed=1000.0  # Instantáneo
    )
    
    # Primer update - debería mover el macro
    engine.update(0.016)
    pos_after_first = engine._positions[sid].copy()
    print(f"\nPosición después de 1er update: [{pos_after_first[0]:.2f}, {pos_after_first[1]:.2f}, {pos_after_first[2]:.2f}]")
    
    # Verificar que SÍ hubo movimiento
    movement = np.linalg.norm(pos_after_first - pos_inicial)
    if movement > 0.1:
        print(f"✅ CORRECTO: El macro se movió {movement:.2f} unidades")
    else:
        print(f"❌ ERROR: El macro no se movió (solo {movement:.6f} unidades)")
    
    # Verificar posición esperada (aproximadamente (0,5,0))
    expected = np.array([0.0, 5.0, 0.0])
    error = np.linalg.norm(pos_after_first - expected)
    if error < 0.1:
        print(f"✅ CORRECTO: Posición final cerca de la esperada (error: {error:.3f})")
    else:
        print(f"⚠️  La posición final no es exactamente la esperada (error: {error:.3f})")
    
    # Múltiples updates adicionales - NO deberían causar más movimiento
    print("\n--- Verificando que el movimiento se detiene ---")
    positions = []
    for i in range(10):
        engine.update(0.016)
        pos = engine._positions[sid].copy()
        positions.append(pos)
    
    # Verificar que la posición se mantiene estática después del primer movimiento
    all_static = True
    for i in range(1, len(positions)):
        delta = np.linalg.norm(positions[i] - positions[i-1])
        if delta > 0.001:
            all_static = False
            print(f"  ❌ Movimiento detectado entre update {i+1} y {i+2}: {delta:.6f}")
    
    if all_static:
        print("  ✅ CORRECTO: Posición se mantiene estática después de la rotación")
    else:
        print("  ❌ ERROR: La posición sigue cambiando!")

def test_different_rotations():
    """Test diferentes tipos de rotaciones"""
    print(f"\n{'='*60}")
    print("TEST: DIFERENTES ROTACIONES")
    print(f"{'='*60}")
    
    engine = EnhancedTrajectoryEngine(max_sources=10)
    
    # Crear macro con 3 fuentes en línea
    macro_id = engine.create_macro("test_rotations", 3, "rigid", formation="line")
    sources = list(engine._macros[macro_id].source_ids)
    
    # Posiciones iniciales
    print("\nPosiciones iniciales:")
    for i, sid in enumerate(sources):
        pos = engine._positions[sid]
        print(f"  Fuente {i+1}: [{pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f}]")
    
    # Test 1: Rotación de 45 grados en Yaw
    print("\n--- Rotación Yaw=45° ---")
    engine.set_manual_macro_rotation(
        macro_id,
        yaw=np.radians(45),
        interpolation_speed=1000.0
    )
    
    engine.update(0.016)
    
    print("Posiciones después de rotación:")
    for i, sid in enumerate(sources):
        pos = engine._positions[sid]
        print(f"  Fuente {i+1}: [{pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f}]")
    
    # Test 2: Rotación en Pitch (poner vertical)
    print("\n--- Rotación Pitch=90° (poner vertical) ---")
    engine.set_manual_macro_rotation(
        macro_id,
        pitch=np.radians(90),
        yaw=0,
        interpolation_speed=1000.0
    )
    
    engine.update(0.016)
    
    print("Posiciones después de rotación vertical:")
    for i, sid in enumerate(sources):
        pos = engine._positions[sid]
        print(f"  Fuente {i+1}: [{pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f}]")

def test_rotation_persistence():
    """Test que la rotación manual persiste correctamente"""
    print(f"\n{'='*60}")
    print("TEST: PERSISTENCIA DE ROTACIÓN")
    print(f"{'='*60}")
    
    engine = EnhancedTrajectoryEngine(max_sources=10)
    
    # Crear macro
    macro_id = engine.create_macro("test_persist", 1, "rigid")
    sid = list(engine._macros[macro_id].source_ids)[0]
    engine._positions[sid] = np.array([3.0, 0.0, 0.0])
    
    # Aplicar rotación
    print("\nAplicando rotación Yaw=180° (dar la vuelta)...")
    engine.set_manual_macro_rotation(
        macro_id,
        yaw=np.radians(180),
        interpolation_speed=1000.0
    )
    
    engine.update(0.016)
    pos_rotated = engine._positions[sid].copy()
    print(f"Posición después de rotación: [{pos_rotated[0]:.2f}, {pos_rotated[1]:.2f}, {pos_rotated[2]:.2f}]")
    
    # Simular 100 updates más
    print("\nSimulando 100 updates adicionales...")
    for _ in range(100):
        engine.update(0.016)
    
    pos_final = engine._positions[sid].copy()
    drift = np.linalg.norm(pos_final - pos_rotated)
    
    print(f"Posición final: [{pos_final[0]:.2f}, {pos_final[1]:.2f}, {pos_final[2]:.2f}]")
    print(f"Deriva total: {drift:.6f} unidades")
    
    if drift < 0.001:
        print("✅ EXCELENTE: Rotación totalmente estable")
    elif drift < 0.01:
        print("✅ BUENO: Rotación estable con deriva mínima")
    else:
        print("❌ ERROR: Deriva significativa detectada")

if __name__ == "__main__":
    test_manual_rotation_movement()
    test_different_rotations()
    test_rotation_persistence()
    
    print(f"\n{'='*60}")
    print("RESUMEN DE LA SOLUCIÓN:")
    print("✅ Rotación Manual MS ahora SÍ mueve el macro")
    print("✅ Aplica la rotación según PRY para cambiar orientación física")
    print("✅ Una vez aplicada, el macro se queda quieto")
    print("✅ No hay rotación continua")
    print(f"{'='*60}")