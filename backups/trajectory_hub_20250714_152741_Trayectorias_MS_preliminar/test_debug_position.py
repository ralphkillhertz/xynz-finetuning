#!/usr/bin/env python3
"""
Debug del problema de posición
"""
import numpy as np
from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine

def debug_position_issue():
    """Debug detallado del problema"""
    
    print("=== DEBUG DE POSICIÓN ===\n")
    
    engine = EnhancedTrajectoryEngine(max_sources=100)
    
    # Crear macro
    print("1. Creando macro...")
    macro_id = engine.create_macro(
        name="debug",
        source_count=4,
        formation="circle",
        spacing=2.0
    )
    
    # Ver qué fuentes pertenecen al macro
    macro = engine._macros[macro_id]
    print(f"\n2. Fuentes del macro: {list(macro.source_ids)}")
    
    # Ver posiciones iniciales
    print("\n3. Posiciones iniciales:")
    for sid in macro.source_ids:
        if sid < len(engine._positions):
            pos = engine._positions[sid]
            print(f"   Fuente {sid}: {pos}")
            
    # Calcular centro
    center = engine.get_macro_center(macro_id)
    print(f"\n4. Centro calculado: {center}")
    
    # Mover macro
    new_pos = np.array([5.0, 0.0, 0.0])
    print(f"\n5. Moviendo a: {new_pos}")
    engine.move_macro_center(macro_id, new_pos)
    
    # Ver posiciones después de mover
    print("\n6. Posiciones después de mover:")
    for sid in macro.source_ids:
        if sid < len(engine._positions):
            pos = engine._positions[sid]
            print(f"   Fuente {sid}: {pos}")
            
    # Ver posición 0 (que no debería estar en el macro)
    print(f"\n7. Fuente 0 (no en macro): {engine._positions[0]}")
    
    # Ajustar spacing
    print("\n8. Ajustando spacing...")
    engine.adjust_macro_spacing(macro_id, 4.0)
    
    # Ver posiciones finales
    print("\n9. Posiciones después de ajustar spacing:")
    for sid in macro.source_ids:
        if sid < len(engine._positions):
            pos = engine._positions[sid]
            print(f"   Fuente {sid}: {pos}")
            
    center_final = engine.get_macro_center(macro_id)
    print(f"\n10. Centro final: {center_final}")

if __name__ == "__main__":
    debug_position_issue()