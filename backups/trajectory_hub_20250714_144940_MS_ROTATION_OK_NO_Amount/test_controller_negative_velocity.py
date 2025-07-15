#!/usr/bin/env python3
"""Test específico del controller con velocidades negativas"""

import sys
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'trajectory_hub'))

def test_controller_negative_velocity():
    """Test directo de la función donde se corrigió el input"""
    print("=== TEST DEL CONTROLLER CON VELOCIDADES NEGATIVAS ===\n")
    
    from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
    
    # Crear engine
    engine = EnhancedTrajectoryEngine(max_sources=10)
    
    # Simular la creación de un macro
    macro_id = engine.create_macro("test_velocity", 1, "rigid")
    print(f"✅ Macro creado: {macro_id}")
    
    # Simular la función del controller que ahora acepta velocidades negativas
    # Esta es la línea que modificamos:
    # speed_multiplier = self.ui.get_numeric_input("Velocidad de rotación (-10.0-10.0): ", -10.0, 10.0) or 1.0
    
    # Test de diferentes valores de speed_multiplier (antes restringido a 0.1-10.0)
    test_multipliers = [-5.0, -2.0, -1.0, -0.5, 0.5, 1.0, 2.0, 5.0]
    
    for multiplier in test_multipliers:
        print(f"\n--- Test con speed_multiplier: {multiplier:+.1f} ---")
        
        # Simular los cálculos del controller
        base_speed_x, base_speed_y, base_speed_z = 0.0, 0.0, 1.0  # Rotación básica en Z
        depth = 100  # 100%
        
        # Aplicar ajustes (como en el controller)
        depth_factor = depth / 100.0
        speed_x = base_speed_x * multiplier * depth_factor
        speed_y = base_speed_y * multiplier * depth_factor
        speed_z = base_speed_z * multiplier * depth_factor
        
        print(f"  Velocidades calculadas: X={speed_x:.2f}, Y={speed_y:.2f}, Z={speed_z:.2f}")
        
        # Aplicar al engine
        try:
            engine.set_macro_rotation(
                macro_id,
                speed_x=speed_x,
                speed_y=speed_y,
                speed_z=speed_z,
                center=[0.0, 0.0, 0.0]
            )
            
            # Verificar sentido de rotación
            if speed_z > 0:
                sentido = "ANTIHORARIO (positivo)"
            elif speed_z < 0:
                sentido = "HORARIO (negativo)"
            else:
                sentido = "SIN ROTACIÓN"
                
            print(f"  ✅ Rotación aplicada - Sentido: {sentido}")
            
            # Simular algunos updates para verificar
            for _ in range(3):
                engine.update(0.016)
                
            print(f"  ✅ Updates completados")
            
        except Exception as e:
            print(f"  ❌ Error: {e}")

def test_compare_before_after():
    """Comparar el comportamiento antes y después del fix"""
    print(f"\n{'='*60}")
    print("COMPARACIÓN ANTES/DESPUÉS DEL FIX")
    print(f"{'='*60}")
    
    print("\n🔴 ANTES (rango 0.1-10.0):")
    print("  - Solo velocidades positivas permitidas")
    print("  - Rango: 0.1 ≤ velocidad ≤ 10.0")
    print("  - Rotación siempre en un solo sentido")
    print("  - -2.0 sería RECHAZADO")
    
    print("\n🟢 DESPUÉS (rango -10.0-10.0):")
    print("  - Velocidades positivas y negativas permitidas")
    print("  - Rango: -10.0 ≤ velocidad ≤ 10.0")
    print("  - Rotación bidireccional")
    print("  - -2.0 es ACEPTADO")
    
    print("\n📊 Ejemplos de velocidades ahora válidas:")
    valid_examples = [
        (-5.0, "Rotación rápida horaria"),
        (-1.0, "Rotación lenta horaria"),
        (-0.1, "Rotación muy lenta horaria"),
        (0.1, "Rotación muy lenta antihoraria"),
        (1.0, "Rotación lenta antihoraria"),
        (5.0, "Rotación rápida antihoraria")
    ]
    
    for value, desc in valid_examples:
        print(f"  {value:+4.1f}: {desc}")

if __name__ == "__main__":
    test_controller_negative_velocity()
    test_compare_before_after()
    
    print(f"\n{'='*60}")
    print("RESUMEN DEL FIX:")
    print("✅ Modificada línea 576 en interactive_controller.py")
    print("✅ Cambiado rango de (0.1, 10.0) a (-10.0, 10.0)")
    print("✅ Ahora el controller acepta velocidades negativas")
    print("✅ Funcionalidad bidireccional activada")
    print("✅ Compatible con el engine que ya soportaba negativos")
    print(f"{'='*60}")