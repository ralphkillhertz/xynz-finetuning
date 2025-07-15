#!/usr/bin/env python3
"""
Prueba de movimiento de macros
"""
import numpy as np
from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
import time

def test_macro_movement():
    """Probar el movimiento de macros"""
    
    print("=== PRUEBA DE MOVIMIENTO DE MACROS ===\n")
    
    engine = EnhancedTrajectoryEngine(max_sources=100)
    
    # Crear un macro
    print("1. Creando macro con formación círculo...")
    macro_id = engine.create_macro(
        name="test_move",
        source_count=8,
        formation="circle",
        spacing=2.0
    )
    
    print(f"   ✅ Macro creado: {macro_id}")
    
    # Obtener centro inicial
    center = engine.get_macro_center(macro_id)
    print(f"\n2. Centro inicial: X={center[0]:.2f}, Y={center[1]:.2f}, Z={center[2]:.2f}")
    
    # Mover a diferentes posiciones
    print("\n3. Probando movimientos...")
    
    test_positions = [
        ("Frente (5m)", np.array([0.0, 0.0, 5.0])),
        ("Derecha y arriba", np.array([5.0, 2.0, 0.0])),
        ("Esquina", np.array([4.0, 0.0, 4.0])),
        ("Vuelta al origen", np.array([0.0, 0.0, 0.0]))
    ]
    
    for name, new_pos in test_positions:
        print(f"\n   Moviendo a {name}...")
        success = engine.move_macro_center(macro_id, new_pos)
        
        if success:
            # Verificar
            actual_center = engine.get_macro_center(macro_id)
            print(f"   ✅ Movido a: X={actual_center[0]:.2f}, Y={actual_center[1]:.2f}, Z={actual_center[2]:.2f}")
            
            # Verificar que todas las fuentes se movieron
            print("   Verificando fuentes:")
            for i in range(3):  # Mostrar solo las primeras 3
                pos = engine._positions[i]
                print(f"     Fuente {i}: X={pos[0]:.2f}, Y={pos[1]:.2f}, Z={pos[2]:.2f}")
                
            time.sleep(1)  # Pausa para observar en SPAT
        else:
            print(f"   ❌ Error al mover a {name}")
    
    # Prueba de desplazamiento relativo
    print("\n4. Probando desplazamiento relativo...")
    current = engine.get_macro_center(macro_id)
    offset = np.array([2.0, 1.0, 3.0])
    new_pos = current + offset
    
    engine.move_macro_center(macro_id, new_pos)
    final = engine.get_macro_center(macro_id)
    
    print(f"   Desde: {current}")
    print(f"   Offset: {offset}")
    print(f"   Final: {final}")
    
    print("\n✨ Prueba completada")

if __name__ == "__main__":
    test_macro_movement()