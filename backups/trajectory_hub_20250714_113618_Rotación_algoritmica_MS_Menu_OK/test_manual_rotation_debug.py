#!/usr/bin/env python3
"""Test detallado de rotación manual con debug"""

import sys
import time
import numpy as np
from pathlib import Path

# Agregar el directorio al path
sys.path.insert(0, str(Path(__file__).parent / 'trajectory_hub'))

from core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
from core.spat_osc_bridge import SpatOSCBridge

def test_manual_rotation():
    print("=== TEST DE ROTACIÓN MANUAL CON DEBUG ===\n")
    
    # Crear engine y bridge
    engine = EnhancedTrajectoryEngine(max_sources=10)
    # El engine ya tiene su propio OSC bridge inicializado
    
    # Crear macro con 4 fuentes
    macro_id = engine.create_macro(
        name="test_rotation",
        source_count=4,
        behavior="rigid",
        formation="grid",
        spacing=4.0
    )
    
    print(f"✅ Macro creado: {macro_id}")
    print(f"   Fuentes: {engine._macros[macro_id].source_ids}")
    
    # Verificar posiciones iniciales
    print("\n📍 Posiciones iniciales:")
    for i, sid in enumerate(engine._macros[macro_id].source_ids):
        pos = engine._positions[sid]
        print(f"   Fuente {sid}: [{pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f}]")
    
    # Configurar rotación manual (90 grados en Y)
    print("\n🔄 Configurando rotación manual...")
    yaw_rad = np.radians(90)
    success = engine.set_manual_macro_rotation(
        macro_id,
        yaw=yaw_rad,
        pitch=0,
        roll=0,
        interpolation_speed=1.0  # Instantáneo para test
    )
    
    if not success:
        print("❌ Error configurando rotación")
        return
    
    # Verificar que el componente existe
    print("\n🔍 Verificando componentes de rotación:")
    for sid in engine._macros[macro_id].source_ids:
        if sid in engine.motion_states:
            motion = engine.motion_states[sid]
            comps = list(motion.active_components.keys())
            print(f"   Fuente {sid}: {comps}")
            
            # Verificar estado del componente
            if 'manual_macro_rotation' in motion.active_components:
                rot = motion.active_components['manual_macro_rotation']
                print(f"      - enabled: {rot.enabled}")
                print(f"      - target_yaw: {np.degrees(rot.target_yaw):.1f}°")
                print(f"      - interpolation_speed: {rot.interpolation_speed}")
                print(f"      - center: {rot.center}")
    
    # Hacer varios updates para ver el progreso
    print("\n🔄 Ejecutando updates...")
    dt = 0.016  # 60 FPS
    
    for i in range(10):
        print(f"\n--- Update {i+1} ---")
        
        # Update del engine
        engine.update(dt)
        
        # Mostrar posiciones actuales
        for j, sid in enumerate(engine._macros[macro_id].source_ids):
            pos = engine._positions[sid]
            print(f"   Fuente {sid}: [{pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f}]")
            
            # Verificar si hay deltas
            if sid in engine.motion_states:
                motion = engine.motion_states[sid]
                if hasattr(motion, '_last_deltas'):
                    print(f"      Deltas: {motion._last_deltas}")
        
        time.sleep(0.1)
    
    # Verificar posiciones finales
    print("\n📍 Posiciones finales (deberían haber rotado 90°):")
    print("   Esperado: (2,2,0) → (0,2,-2)")
    print("   Esperado: (-2,2,0) → (0,2,2)")
    print("   Esperado: (-2,-2,0) → (0,-2,2)")
    print("   Esperado: (2,-2,0) → (0,-2,-2)")
    print("\n   Actual:")
    for i, sid in enumerate(engine._macros[macro_id].source_ids):
        pos = engine._positions[sid]
        print(f"   Fuente {sid}: [{pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f}]")

if __name__ == "__main__":
    test_manual_rotation()