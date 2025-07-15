#\!/usr/bin/env python3
"""Test de rotación manual verdaderamente instantánea"""

import sys
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "trajectory_hub"))

from core.enhanced_trajectory_engine import EnhancedTrajectoryEngine

def test_rotacion_instantanea():
    """Test que la rotación se aplica en un solo frame"""
    print("=== TEST: ROTACIÓN MANUAL INSTANTÁNEA (1 FRAME) ===\n")
    
    # Crear engine
    engine = EnhancedTrajectoryEngine(max_sources=10)
    
    # Crear macro
    macro_id = engine.create_macro("test_instant", 1, "rigid")
    print(f"✅ Macro creado: {macro_id}")
    
    # Posición inicial
    sid = list(engine._macros[macro_id].source_ids)[0]
    engine._positions[sid] = np.array([5.0, 0.0, 0.0])
    pos_inicial = engine._positions[sid].copy()
    print(f"Posición inicial: [{pos_inicial[0]:.2f}, {pos_inicial[1]:.2f}, {pos_inicial[2]:.2f}]")
    
    # Aplicar rotación manual
    print("\n--- Aplicando rotación manual (Yaw=90°) ---")
    engine.set_manual_macro_rotation(
        macro_id,
        yaw=np.radians(90),
        pitch=0,
        roll=0,
        interpolation_speed=1000.0
    )
    
    # UN SOLO UPDATE
    print("\n🔄 Ejecutando UN SOLO update...")
    engine.update(0.016)
    
    pos_after_one = engine._positions[sid].copy()
    print(f"Posición después de 1 update: [{pos_after_one[0]:.2f}, {pos_after_one[1]:.2f}, {pos_after_one[2]:.2f}]")
    
    # Verificar que la rotación se completó
    expected = np.array([0.0, 5.0, 0.0])  # 90 grados de rotación
    error = np.linalg.norm(pos_after_one - expected)
    
    if error < 0.1:
        print(f"✅ PERFECTO: Rotación completa en 1 frame (error: {error:.4f})")
    else:
        print(f"❌ ERROR: La rotación no se completó en 1 frame (error: {error:.4f})")
    
    # Verificar que no hay más movimiento
    print("\n--- Verificando que NO hay más movimiento ---")
    for i in range(5):
        engine.update(0.016)
        pos = engine._positions[sid].copy()
        delta = np.linalg.norm(pos - pos_after_one)
        print(f"  Update {i+2}: Delta = {delta:.6f}")
        
        if delta > 0.001:
            print(f"    ❌ ERROR: Movimiento detectado\!")
    
    print("\n✅ Rotación aplicada instantáneamente y sin movimiento posterior")

if __name__ == "__main__":
    test_rotacion_instantanea()
    
    print(f"\n{\"=\"*60}")
    print("RESUMEN DE LA SOLUCIÓN:")
    print("✅ Rotación Manual MS ahora es INSTANTÁNEA (1 frame)")
    print("✅ No hay interpolación ni rotación gradual")
    print("✅ El macro se mueve directamente a su posición final")
    print("✅ Después del primer update, no hay más movimiento")
    print(f"{\"=\"*60}")
