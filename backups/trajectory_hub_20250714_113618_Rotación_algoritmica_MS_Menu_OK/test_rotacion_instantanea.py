#!/usr/bin/env python3
"""Test de rotación instantánea para verificar el cálculo"""

import sys
import numpy as np
from pathlib import Path

# Agregar el directorio al path
sys.path.insert(0, str(Path(__file__).parent / 'trajectory_hub'))

from core.enhanced_trajectory_engine import EnhancedTrajectoryEngine

def test_rotacion_instantanea():
    print("=== TEST DE ROTACIÓN INSTANTÁNEA ===\n")
    
    # Crear engine
    engine = EnhancedTrajectoryEngine(max_sources=10)
    
    # Crear macro simple con 2 fuentes
    macro_id = engine.create_macro(
        name="test_instant",
        source_count=2,
        behavior="rigid",
        formation="line",
        spacing=4.0
    )
    
    # Obtener posiciones iniciales
    source_ids = list(engine._macros[macro_id].source_ids)
    
    print("📍 Posiciones iniciales:")
    for sid in source_ids:
        pos = engine._positions[sid]
        print(f"   Fuente {sid}: [{pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f}]")
    
    # Configurar rotación instantánea
    print("\n🔄 Configurando rotación instantánea de 90° en Y...")
    success = engine.set_manual_macro_rotation(
        macro_id,
        yaw=np.radians(90),
        pitch=0,
        roll=0,
        interpolation_speed=1.0  # Instantáneo
    )
    
    if not success:
        print("❌ Error configurando rotación")
        return
    
    # Un solo update con dt grande
    print("\n⏱️  Ejecutando UN update...")
    engine.update(1.0)  # dt = 1 segundo para asegurar interpolación completa
    
    # Posiciones finales
    print("\n📍 Posiciones después de 1 update:")
    for sid in source_ids:
        pos = engine._positions[sid]
        print(f"   Fuente {sid}: [{pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f}]")
    
    # Verificar manualmente
    print("\n📐 Verificación manual:")
    print("   Si el centro está en (0, 0, 0):")
    print("   - Punto en (2, 0, 0) debería ir a (0, 0, -2) después de 90° en Y")
    print("   - Punto en (-2, 0, 0) debería ir a (0, 0, 2) después de 90° en Y")

if __name__ == "__main__":
    test_rotacion_instantanea()