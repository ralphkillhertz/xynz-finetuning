#!/usr/bin/env python3
"""Test de rotación 3D con debug detallado"""

import sys
import numpy as np
from pathlib import Path

# Agregar el directorio al path
sys.path.insert(0, str(Path(__file__).parent / 'trajectory_hub'))

from core.enhanced_trajectory_engine import EnhancedTrajectoryEngine

def calcular_rotacion_esperada(pos_inicial, centro, yaw_rad):
    """Calcula la posición esperada después de rotar"""
    # Posición relativa al centro
    rel_pos = pos_inicial - centro
    
    # Matriz de rotación Y (yaw)
    cy, sy = np.cos(yaw_rad), np.sin(yaw_rad)
    ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    
    # Aplicar rotación
    rel_pos_rotada = ry @ rel_pos
    
    # Posición absoluta final
    return centro + rel_pos_rotada

def test_rotacion_3d():
    print("=== TEST DE ROTACIÓN 3D CON DEBUG ===\n")
    
    # Crear engine
    engine = EnhancedTrajectoryEngine(max_sources=10)
    
    # Crear macro
    macro_id = engine.create_macro(
        name="test_rot3d",
        source_count=4,
        behavior="rigid",
        formation="grid",
        spacing=4.0
    )
    
    # Obtener posiciones iniciales
    source_ids = list(engine._macros[macro_id].source_ids)
    pos_iniciales = []
    
    print("📍 Posiciones iniciales:")
    for sid in source_ids:
        pos = engine._positions[sid].copy()
        pos_iniciales.append(pos)
        print(f"   Fuente {sid}: [{pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f}]")
    
    # Calcular centro del macro
    centro = np.mean(pos_iniciales, axis=0)
    print(f"\n📐 Centro del macro: [{centro[0]:.2f}, {centro[1]:.2f}, {centro[2]:.2f}]")
    
    # Calcular posiciones esperadas para rotación de 90° en Y
    yaw_rad = np.radians(90)
    print(f"\n🎯 Posiciones esperadas después de rotar 90° en Y:")
    pos_esperadas = []
    for i, pos in enumerate(pos_iniciales):
        pos_esp = calcular_rotacion_esperada(pos, centro, yaw_rad)
        pos_esperadas.append(pos_esp)
        print(f"   Fuente {source_ids[i]}: [{pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f}] → [{pos_esp[0]:.2f}, {pos_esp[1]:.2f}, {pos_esp[2]:.2f}]")
    
    # Configurar rotación manual
    print("\n🔄 Configurando rotación manual...")
    success = engine.set_manual_macro_rotation(
        macro_id,
        yaw=yaw_rad,
        pitch=0,
        roll=0,
        interpolation_speed=0.1  # Más rápido para el test
    )
    
    if not success:
        print("❌ Error configurando rotación")
        return
    
    # Verificar componente de rotación
    print("\n🔍 Verificando componente de rotación:")
    sid = source_ids[0]
    if sid in engine.motion_states:
        motion = engine.motion_states[sid]
        if 'manual_macro_rotation' in motion.active_components:
            rot = motion.active_components['manual_macro_rotation']
            print(f"   - Centro de rotación: [{rot.center[0]:.2f}, {rot.center[1]:.2f}, {rot.center[2]:.2f}]")
            print(f"   - Target YAW: {np.degrees(rot.target_yaw):.1f}°")
            print(f"   - Interpolation speed: {rot.interpolation_speed}")
    
    # Ejecutar rotación
    print("\n⏱️  Ejecutando rotación...")
    dt = 0.016  # 60 FPS
    
    # Mostrar primeros pasos
    for i in range(5):
        engine.update(dt)
        print(f"\n--- Update {i+1} ---")
        for j, sid in enumerate(source_ids):
            pos = engine._positions[sid]
            print(f"   Fuente {sid}: [{pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f}]")
    
    # Completar rotación
    for i in range(95):  # Total 100 updates
        engine.update(dt)
    
    # Posiciones finales
    print(f"\n📍 Posiciones finales después de 100 updates:")
    pos_finales = []
    for sid in source_ids:
        pos = engine._positions[sid].copy()
        pos_finales.append(pos)
        print(f"   Fuente {sid}: [{pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f}]")
    
    # Comparar con esperado
    print("\n📊 Comparación con valores esperados:")
    for i, sid in enumerate(source_ids):
        pos_final = pos_finales[i]
        pos_esp = pos_esperadas[i]
        error = np.linalg.norm(pos_final - pos_esp)
        print(f"   Fuente {sid}: Error = {error:.3f}")
        if error > 0.5:
            print(f"      Esperado: [{pos_esp[0]:.2f}, {pos_esp[1]:.2f}, {pos_esp[2]:.2f}]")
            print(f"      Obtenido: [{pos_final[0]:.2f}, {pos_final[1]:.2f}, {pos_final[2]:.2f}]")

if __name__ == "__main__":
    test_rotacion_3d()