#!/usr/bin/env python3
"""Test de rotación manual completa con más iteraciones"""

import sys
import time
import numpy as np
from pathlib import Path

# Agregar el directorio al path
sys.path.insert(0, str(Path(__file__).parent / 'trajectory_hub'))

from core.enhanced_trajectory_engine import EnhancedTrajectoryEngine

def test_rotation_completa():
    print("=== TEST DE ROTACIÓN MANUAL COMPLETA ===\n")
    
    # Crear engine
    engine = EnhancedTrajectoryEngine(max_sources=10)
    
    # Crear macro con 4 fuentes
    macro_id = engine.create_macro(
        name="test_rotation",
        source_count=4,
        behavior="rigid",
        formation="grid",
        spacing=4.0
    )
    
    print(f"✅ Macro creado: {macro_id}")
    
    # Mostrar posiciones iniciales
    print("\n📍 Posiciones iniciales:")
    for sid in engine._macros[macro_id].source_ids:
        pos = engine._positions[sid]
        print(f"   Fuente {sid}: [{pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f}]")
    
    # Configurar rotación manual con velocidad más alta
    print("\n🔄 Configurando rotación manual (90° en Y)...")
    success = engine.set_manual_macro_rotation(
        macro_id,
        yaw=np.radians(90),
        pitch=0,
        roll=0,
        interpolation_speed=0.05  # Más lento para ver el progreso
    )
    
    if not success:
        print("❌ Error configurando rotación")
        return
    
    # Hacer muchos más updates
    print("\n⏱️  Ejecutando rotación...")
    dt = 0.016  # 60 FPS
    updates = 0
    max_updates = 200  # Suficientes para completar la rotación
    
    while updates < max_updates:
        engine.update(dt)
        updates += 1
        
        # Mostrar progreso cada 20 updates
        if updates % 20 == 0:
            print(f"\n--- Update {updates} ---")
            for sid in engine._macros[macro_id].source_ids:
                pos = engine._positions[sid]
                print(f"   Fuente {sid}: [{pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f}]")
        
        time.sleep(0.01)  # Pequeño delay para no saturar
    
    # Posiciones finales
    print(f"\n📍 Posiciones finales después de {updates} updates:")
    for sid in engine._macros[macro_id].source_ids:
        pos = engine._positions[sid]
        print(f"   Fuente {sid}: [{pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f}]")
    
    # Verificar si la rotación se completó
    print("\n🔍 Verificando rotación:")
    # El centro está en (-2, -2, 0)
    # Fuente 0: (-4,-4,0) relativo al centro: (-2,-2,0)
    # Después de 90° en Y debería estar en: (-2,0,-2) + centro = (-4,-2,-2)
    
    expected = [
        (-4, -2, -2),  # Fuente 0
        (0, -2, -2),   # Fuente 1  
        (-4, -2, 2),   # Fuente 2
        (0, -2, 2),    # Fuente 3
    ]
    
    print("\n   Posiciones esperadas vs actuales:")
    for i, sid in enumerate(engine._macros[macro_id].source_ids):
        pos = engine._positions[sid]
        exp = expected[i]
        error = np.sqrt((pos[0]-exp[0])**2 + (pos[1]-exp[1])**2 + (pos[2]-exp[2])**2)
        print(f"   Fuente {sid}: Esperado {exp} -> Actual [{pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f}] (error: {error:.3f})")

if __name__ == "__main__":
    test_rotation_completa()