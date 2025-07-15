#!/usr/bin/env python3
"""
Prueba de ajuste de spacing
"""
import numpy as np
from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
import time

def test_spacing_adjustment():
    """Probar creación y ajuste de spacing de un macro"""
    
    print("=== PRUEBA DE AJUSTE DE SPACING ===\n")
    
    engine = EnhancedTrajectoryEngine(max_sources=100)
    
    # Crear un macro con círculo
    print("1. Creando macro con formación círculo (radio=2.0)...")
    macro_id = engine.create_macro(
        name="test_circle",
        source_count=8,
        formation="circle",
        spacing=2.0
    )
    
    print(f"   ✅ Macro creado: {macro_id}")
    
    # Mostrar posiciones iniciales
    print("\n2. Posiciones iniciales (radio=2.0):")
    for i in range(8):
        pos = engine._positions[i]
        r = np.sqrt(pos[0]**2 + pos[1]**2)
        print(f"   Fuente {i}: x={pos[0]:6.3f}, y={pos[1]:6.3f}, r={r:.3f}")
    
    # Esperar un poco
    time.sleep(1)
    
    # Ajustar spacing
    print("\n3. Ajustando spacing a 5.0...")
    success = engine.adjust_macro_spacing(macro_id, 5.0)
    if success:
        print("   ✅ Spacing ajustado exitosamente")
    else:
        print("   ❌ Error al ajustar spacing")
        return
    
    # Mostrar nuevas posiciones
    print("\n4. Posiciones después del ajuste (radio=5.0):")
    for i in range(8):
        pos = engine._positions[i]
        r = np.sqrt(pos[0]**2 + pos[1]**2)
        print(f"   Fuente {i}: x={pos[0]:6.3f}, y={pos[1]:6.3f}, r={r:.3f}")
    
    # Verificar información del macro
    print("\n5. Información del macro:")
    macro_info = engine.select_macro(macro_id)
    if macro_info:
        print(f"   Nombre: {macro_info['name']}")
        print(f"   Formación: {macro_info['formation']}")
        print(f"   Spacing: {macro_info['spacing']}")
        print(f"   Fuentes: {macro_info['num_sources']}")
    
    print("\n✨ Prueba completada exitosamente")

if __name__ == "__main__":
    test_spacing_adjustment()