#!/usr/bin/env python3
"""Test de velocidades negativas para cambio de sentido de rotación"""

import sys
import time
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'trajectory_hub'))

from core.enhanced_trajectory_engine import EnhancedTrajectoryEngine

def test_velocidades_negativas():
    print("=== TEST DE VELOCIDADES NEGATIVAS ===\n")
    
    # Crear engine
    engine = EnhancedTrajectoryEngine(max_sources=10)
    
    # Velocidades a probar (positivas y negativas)
    velocidades = [
        {"name": "Positiva lenta", "speed_z": 0.5},
        {"name": "Positiva rápida", "speed_z": 2.0},
        {"name": "Negativa lenta", "speed_z": -0.5},
        {"name": "Negativa rápida", "speed_z": -2.0},
        {"name": "X negativo", "speed_x": -1.0},
        {"name": "Y negativo", "speed_y": -1.0},
        {"name": "Combinado", "speed_x": 0.5, "speed_y": -0.5, "speed_z": 1.0}
    ]
    
    for i, vel_config in enumerate(velocidades):
        print(f"\n{'='*60}")
        print(f"TEST {i+1}: {vel_config['name']}")
        print(f"{'='*60}")
        
        # Crear macro único
        macro_id = engine.create_macro(
            name=f"test_neg_{i}",
            source_count=1,
            behavior="rigid"
        )
        
        # Posición inicial
        sid = list(engine._macros[macro_id].source_ids)[0]
        engine._positions[sid] = np.array([3.0, 0.0, 0.0])
        pos_inicial = engine._positions[sid].copy()
        
        # Configurar rotación algorítmica con velocidades negativas
        speed_x = vel_config.get("speed_x", 0.0)
        speed_y = vel_config.get("speed_y", 0.0)
        speed_z = vel_config.get("speed_z", 0.0)
        
        engine.set_macro_rotation(
            macro_id,
            speed_x=speed_x,
            speed_y=speed_y,
            speed_z=speed_z,
            center=[0.0, 0.0, 0.0]
        )
        
        # Simular 2 segundos
        dt = 0.016  # 60 FPS
        tiempo = 0
        updates = 0
        
        print(f"Velocidades: X={speed_x:.2f}, Y={speed_y:.2f}, Z={speed_z:.2f} rad/s")
        print(f"Inicial: [{pos_inicial[0]:.2f}, {pos_inicial[1]:.2f}, {pos_inicial[2]:.2f}]")
        
        posiciones = [pos_inicial.copy()]
        
        while tiempo < 2.0:
            engine.update(dt)
            tiempo += dt
            updates += 1
            
            # Guardar posición cada 0.5 segundos
            if updates % 30 == 0:
                pos = engine._positions[sid].copy()
                posiciones.append(pos)
                print(f"  {tiempo:.1f}s: [{pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f}]")
        
        # Análisis del movimiento
        pos_final = engine._positions[sid]
        print(f"Final: [{pos_final[0]:.2f}, {pos_final[1]:.2f}, {pos_final[2]:.2f}]")
        
        # Verificar dirección de rotación
        if len(posiciones) >= 3:
            # Calcular ángulos en diferentes puntos
            angle_inicial = np.arctan2(posiciones[0][1], posiciones[0][0])
            angle_medio = np.arctan2(posiciones[1][1], posiciones[1][0])
            angle_final = np.arctan2(pos_final[1], pos_final[0])
            
            # Diferencia angular (considerando wrap-around)
            diff1 = angle_medio - angle_inicial
            diff2 = angle_final - angle_medio
            
            # Normalizar a [-π, π]
            diff1 = ((diff1 + np.pi) % (2 * np.pi)) - np.pi
            diff2 = ((diff2 + np.pi) % (2 * np.pi)) - np.pi
            
            sentido = "HORARIO" if (diff1 + diff2) < 0 else "ANTIHORARIO"
            
            print(f"Sentido de rotación: {sentido}")
            
            if speed_z > 0:
                expected = "ANTIHORARIO"
            elif speed_z < 0:
                expected = "HORARIO"
            else:
                expected = "SIN ROTACIÓN Z"
            
            if speed_z != 0:
                resultado = "✅ CORRECTO" if sentido == expected else "❌ ERROR"
                print(f"Esperado: {expected} | Resultado: {resultado}")
        
        print(f"Desplazamiento total: {np.linalg.norm(pos_final - pos_inicial):.3f}m")
        
    print(f"\n{'='*60}")
    print("RESUMEN:")
    print("- Las velocidades negativas deben invertir el sentido de rotación")
    print("- speed_z > 0: Rotación antihoraria")
    print("- speed_z < 0: Rotación horaria")
    print("- Lo mismo aplica para speed_x y speed_y en sus respectivos ejes")

def test_cambio_direccion_dinamico():
    """Test para cambiar dirección dinámicamente"""
    print(f"\n{'='*60}")
    print("TEST DE CAMBIO DINÁMICO DE DIRECCIÓN")
    print(f"{'='*60}")
    
    engine = EnhancedTrajectoryEngine(max_sources=10)
    
    # Crear macro
    macro_id = engine.create_macro(
        name="test_dinamico",
        source_count=1,
        behavior="rigid"
    )
    
    sid = list(engine._macros[macro_id].source_ids)[0]
    engine._positions[sid] = np.array([3.0, 0.0, 0.0])
    
    # Simular cambios de velocidad cada segundo
    velocidades_tiempo = [
        (1.0, {"speed_z": 1.0}),    # 1 seg horario
        (1.0, {"speed_z": -1.0}),   # 1 seg antihorario  
        (1.0, {"speed_z": 2.0}),    # 1 seg horario rápido
        (1.0, {"speed_z": -2.0})    # 1 seg antihorario rápido
    ]
    
    dt = 0.016
    tiempo_total = 0
    
    for duracion, vel_config in velocidades_tiempo:
        print(f"\nCambiando a: {vel_config}")
        
        engine.set_macro_rotation(
            macro_id,
            **vel_config,
            center=[0.0, 0.0, 0.0]
        )
        
        pos_inicio = engine._positions[sid].copy()
        tiempo_fase = 0
        
        while tiempo_fase < duracion:
            engine.update(dt)
            tiempo_fase += dt
            tiempo_total += dt
            
        pos_fin = engine._positions[sid].copy()
        angle_inicio = np.arctan2(pos_inicio[1], pos_inicio[0])
        angle_fin = np.arctan2(pos_fin[1], pos_fin[0])
        diff = ((angle_fin - angle_inicio + np.pi) % (2 * np.pi)) - np.pi
        
        sentido = "HORARIO" if diff < 0 else "ANTIHORARIO"
        print(f"  Tiempo: {tiempo_total:.1f}s | Sentido: {sentido} | Rotación: {np.degrees(abs(diff)):.1f}°")

if __name__ == "__main__":
    test_velocidades_negativas()
    test_cambio_direccion_dinamico()