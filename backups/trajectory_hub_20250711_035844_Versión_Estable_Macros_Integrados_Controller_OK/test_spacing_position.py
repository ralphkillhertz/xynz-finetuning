#!/usr/bin/env python3
"""
Prueba de que el ajuste de spacing preserva la posición del macro
"""
import numpy as np
from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
import time

def test_spacing_preserves_position():
    """Verificar que ajustar spacing no cambia la posición del centro"""
    
    print("=== PRUEBA: SPACING DEBE PRESERVAR POSICIÓN ===\n")
    
    engine = EnhancedTrajectoryEngine(max_sources=100)
    
    # Crear un macro
    print("1. Creando macro con formación círculo...")
    macro_id = engine.create_macro(
        name="test_position",
        source_count=8,
        formation="circle",
        spacing=2.0
    )
    
    print(f"   ✅ Macro creado: {macro_id}")
    
    # Mover el macro a una posición específica
    new_position = np.array([5.0, 2.0, 3.0])
    print(f"\n2. Moviendo macro a posición: {new_position}")
    engine.move_macro_center(macro_id, new_position)
    
    # Verificar posición
    center_before = engine.get_macro_center(macro_id)
    print(f"   Centro después de mover: {center_before}")
    
    # Ajustar spacing
    print("\n3. Ajustando spacing de 2.0 a 4.0...")
    engine.adjust_macro_spacing(macro_id, 4.0)
    
    # Verificar que el centro no cambió
    center_after = engine.get_macro_center(macro_id)
    print(f"   Centro después de ajustar spacing: {center_after}")
    
    # Comparar
    difference = np.linalg.norm(center_after - center_before)
    print(f"\n4. Diferencia entre centros: {difference:.6f}")
    
    if difference < 0.01:  # Tolerancia pequeña para errores de redondeo
        print("   ✅ CORRECTO: La posición se mantuvo")
    else:
        print("   ❌ ERROR: La posición cambió!")
        
    # Mostrar algunas posiciones de fuentes para verificar
    print("\n5. Verificación de fuentes (primeras 3):")
    for i in range(3):
        pos = engine._positions[i]
        dist = np.linalg.norm(pos - center_after)
        print(f"   Fuente {i}: pos={pos}, distancia al centro={dist:.2f}")
        
    # Probar con otra formación
    print("\n6. Probando con formación esfera...")
    
    # Crear otro macro
    macro_id2 = engine.create_macro(
        name="test_sphere",
        source_count=20,
        formation="sphere",
        spacing=3.0
    )
    
    # Mover y ajustar spacing
    move_pos = np.array([-4.0, 1.0, -2.0])
    engine.move_macro_center(macro_id2, move_pos)
    
    center_before2 = engine.get_macro_center(macro_id2)
    engine.adjust_macro_spacing(macro_id2, 5.0)
    center_after2 = engine.get_macro_center(macro_id2)
    
    diff2 = np.linalg.norm(center_after2 - center_before2)
    print(f"   Diferencia para esfera: {diff2:.6f}")
    
    if diff2 < 0.01:
        print("   ✅ CORRECTO: Esfera también mantiene posición")
    else:
        print("   ❌ ERROR: Esfera cambió posición")
        
    print("\n✨ Prueba completada")

if __name__ == "__main__":
    test_spacing_preserves_position()