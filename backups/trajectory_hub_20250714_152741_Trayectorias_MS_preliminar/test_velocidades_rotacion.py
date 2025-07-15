#!/usr/bin/env python3
"""Test de diferentes velocidades de rotación"""

import sys
import time
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'trajectory_hub'))

from core.enhanced_trajectory_engine import EnhancedTrajectoryEngine

def test_velocidades():
    print("=== TEST DE VELOCIDADES DE ROTACIÓN ===\n")
    
    # Crear engine
    engine = EnhancedTrajectoryEngine(max_sources=10)
    
    # Diferentes velocidades a probar
    velocidades = [0.05, 0.1, 0.5, 1.0, 2.0]
    
    for vel in velocidades:
        print(f"\n{'='*50}")
        print(f"TEST CON VELOCIDAD: {vel}")
        print(f"{'='*50}")
        
        # Crear macro
        macro_id = engine.create_macro(
            name=f"test_vel_{vel}",
            source_count=1,
            behavior="rigid"
        )
        
        # Posición inicial
        sid = list(engine._macros[macro_id].source_ids)[0]
        engine._positions[sid] = np.array([4.0, 0.0, 0.0])
        pos_inicial = engine._positions[sid].copy()
        
        # Configurar rotación
        engine.set_manual_macro_rotation(
            macro_id,
            yaw=np.radians(90),  # 90 grados
            interpolation_speed=vel
        )
        
        # Forzar centro en origen
        if sid in engine.motion_states and 'manual_macro_rotation' in engine.motion_states[sid].active_components:
            engine.motion_states[sid].active_components['manual_macro_rotation'].center = np.array([0.0, 0.0, 0.0])
        
        # Simular 3 segundos
        dt = 0.016  # 60 FPS
        tiempo = 0
        updates = 0
        
        print(f"Inicial: [{pos_inicial[0]:.2f}, {pos_inicial[1]:.2f}, {pos_inicial[2]:.2f}]")
        
        while tiempo < 3.0:
            engine.update(dt)
            tiempo += dt
            updates += 1
            
            # Mostrar progreso cada segundo
            if updates % 60 == 0:
                pos = engine._positions[sid]
                # Calcular ángulo actual
                angle = np.arctan2(-pos[2], pos[0])
                angle_deg = np.degrees(angle)
                print(f"  {tiempo:.1f}s: [{pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f}] (ángulo: {angle_deg:.1f}°)")
        
        # Final
        pos_final = engine._positions[sid]
        angle_final = np.arctan2(-pos_final[2], pos_final[0])
        angle_final_deg = np.degrees(angle_final)
        print(f"Final: [{pos_final[0]:.2f}, {pos_final[1]:.2f}, {pos_final[2]:.2f}] (ángulo: {angle_final_deg:.1f}°)")
        
        # Tiempo estimado para rotación completa
        if vel > 0:
            tiempo_90_grados = np.pi/2 / vel
            print(f"Tiempo estimado para 90°: {tiempo_90_grados:.2f} segundos")

if __name__ == "__main__":
    test_velocidades()