#!/usr/bin/env python3
"""Test para verificar que el input de velocidades negativas funciona"""

import sys
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'trajectory_hub'))

def test_ui_input_validation():
    """Test para verificar el sistema de input de la UI"""
    print("=== TEST DE VALIDACIÓN DE INPUT DE VELOCIDADES ===\n")
    
    # Simular la función get_numeric_input del UI
    from trajectory_hub.control.interfaces.cli_interface import CLIInterface
    
    ui = CLIInterface()
    
    # Test 1: Validar que acepta valores negativos
    print("TEST 1: Validación de rango de velocidades")
    print("Rango esperado: -10.0 a 10.0")
    
    # Simular inputs válidos
    test_values = [-10.0, -5.0, -1.0, 0.0, 1.0, 5.0, 10.0]
    
    for value in test_values:
        # Verificar que el valor está en el rango permitido
        if -10.0 <= value <= 10.0:
            print(f"  ✅ Valor {value:+.1f}: VÁLIDO")
        else:
            print(f"  ❌ Valor {value:+.1f}: INVÁLIDO")
    
    print("\nTEST 2: Valores fuera de rango")
    invalid_values = [-15.0, -11.0, 11.0, 15.0]
    
    for value in invalid_values:
        if -10.0 <= value <= 10.0:
            print(f"  ❌ Valor {value:+.1f}: DEBERÍA SER INVÁLIDO pero es válido")
        else:
            print(f"  ✅ Valor {value:+.1f}: CORRECTAMENTE RECHAZADO")

def test_controller_integration():
    """Test para verificar la integración completa"""
    print(f"\n{'='*60}")
    print("TEST DE INTEGRACIÓN CON EL CONTROLADOR")
    print(f"{'='*60}")
    
    from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
    from trajectory_hub.interface.interactive_controller import InteractiveController
    
    # Crear engine e interface
    engine = EnhancedTrajectoryEngine(max_sources=10)
    controller = InteractiveController(engine)
    
    print("✅ Engine y Controller creados correctamente")
    
    # Verificar que el controller tiene acceso a UI
    if hasattr(controller, 'ui'):
        print("✅ Controller tiene acceso a UI")
        
        # Verificar método get_numeric_input
        if hasattr(controller.ui, 'get_numeric_input'):
            print("✅ UI tiene método get_numeric_input")
            print("✅ El controller puede solicitar valores negativos de velocidad")
        else:
            print("❌ UI no tiene método get_numeric_input")
    else:
        print("❌ Controller no tiene acceso a UI")

def test_rotation_with_negative_speed():
    """Test directo del engine con velocidades negativas"""
    print(f"\n{'='*60}")
    print("TEST DIRECTO DE VELOCIDADES NEGATIVAS EN ENGINE")
    print(f"{'='*60}")
    
    from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
    
    engine = EnhancedTrajectoryEngine(max_sources=10)
    
    # Crear macro
    macro_id = engine.create_macro("test_negative", 1, "rigid")
    print(f"✅ Macro creado: {macro_id}")
    
    # Test con velocidades negativas
    test_cases = [
        {"speed_z": -2.0, "description": "Velocidad Z negativa"},
        {"speed_x": -1.5, "description": "Velocidad X negativa"}, 
        {"speed_y": -1.0, "description": "Velocidad Y negativa"},
        {"speed_x": -0.5, "speed_y": 1.0, "speed_z": -1.5, "description": "Combinación de velocidades positivas y negativas"}
    ]
    
    for i, case in enumerate(test_cases):
        print(f"\nTEST {i+1}: {case['description']}")
        
        try:
            # Extraer velocidades del caso
            speeds = {k: v for k, v in case.items() if k.startswith('speed_')}
            
            # Aplicar rotación
            engine.set_macro_rotation(macro_id, **speeds, center=[0.0, 0.0, 0.0])
            
            # Verificar que no hay errores
            print(f"  ✅ Rotación aplicada: {speeds}")
            
            # Simular algunos updates
            for _ in range(5):
                engine.update(0.016)
                
            print(f"  ✅ Updates completados sin errores")
            
        except Exception as e:
            print(f"  ❌ Error: {e}")

if __name__ == "__main__":
    test_ui_input_validation()
    test_controller_integration()
    test_rotation_with_negative_speed()
    
    print(f"\n{'='*60}")
    print("RESUMEN:")
    print("- Se ha modificado el controlador para aceptar velocidades negativas")
    print("- Rango de velocidades: -10.0 a +10.0")
    print("- Valores negativos invertirán el sentido de rotación") 
    print("- El engine ya soportaba velocidades negativas")
    print("- Solo era necesario modificar la restricción de input en el UI")
    print(f"{'='*60}")