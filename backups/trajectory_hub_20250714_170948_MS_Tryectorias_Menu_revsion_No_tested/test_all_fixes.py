#!/usr/bin/env python3
"""
Test de todas las correcciones implementadas
"""
import time
import numpy as np
from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine

def test_all_fixes():
    print("=== TEST DE TODAS LAS CORRECCIONES ===\n")
    
    # Crear engine
    engine = EnhancedTrajectoryEngine(max_sources=20)
    
    print("1. TEST DE ÍNDICES - Verificando que el macro comienza en fuente 1")
    print("-" * 60)
    
    # Crear un macro pequeño
    macro_id = engine.create_macro(
        name="test_indices",
        source_count=3,
        formation="line",
        spacing=2.0
    )
    
    # Verificar el macro
    macro_info = engine.select_macro(macro_id)
    print(f"\n   ✓ Macro creado: {macro_info['name']}")
    print(f"   ✓ Source IDs internos (0-based): {macro_info['source_ids']}")
    print(f"   ✓ En SPAT deberían ser fuentes: 1, 2, 3")
    print(f"   ✓ Nombres en SPAT: test_indices_1, test_indices_2, test_indices_3")
    
    # Verificar que las fuentes están desmuteadas (se desmutean al crear macro)
    print("\n   VERIFICAR EN SPAT:")
    print("   • Las fuentes 1, 2, 3 deberían estar DESMUTEADAS (con audio)")
    print("   • Los nombres deberían empezar desde la fuente 1, no desde la 2")
    
    time.sleep(3)
    
    print("\n2. TEST DE ELIMINACIÓN - Posición por defecto y mute")
    print("-" * 60)
    
    # Eliminar el macro
    print("\n   Eliminando macro...")
    engine.delete_macro(macro_id)
    
    print("\n   VERIFICAR EN SPAT:")
    print("   • Las fuentes 1, 2, 3 deberían estar en posición por defecto:")
    print("     - Azimuth = 0°")
    print("     - Elevation = 0°") 
    print("     - Distance = 2m")
    print("   • Las fuentes deberían estar MUTEADAS (sin audio)")
    print("   • Los nombres deberían volver a: Default 1, Default 2, Default 3")
    
    time.sleep(3)
    
    print("\n3. TEST DE ESTADO POR DEFECTO MUTE")
    print("-" * 60)
    
    # Crear fuentes individuales (sin macro)
    print("\n   Creando fuentes individuales...")
    for i in range(3):
        engine.create_source(i + 10, f"test_mute_{i}")
    
    print("\n   VERIFICAR EN SPAT:")
    print("   • Las fuentes 11, 12, 13 deberían estar MUTEADAS por defecto")
    
    time.sleep(2)
    
    # Crear un nuevo macro
    print("\n   Creando un nuevo macro...")
    macro_id2 = engine.create_macro(
        name="test_unmute",
        source_count=4,
        formation="circle",
        spacing=3.0
    )
    
    print("\n   VERIFICAR EN SPAT:")
    print("   • Las nuevas fuentes del macro deberían estar DESMUTEADAS")
    print("   • Los nombres deberían ser: test_unmute_1, test_unmute_2, etc.")
    
    print("\n4. RESUMEN DE CAMBIOS")
    print("-" * 60)
    print("   ✅ Los índices ahora comienzan desde la fuente 1 (no desde la 2)")
    print("   ✅ Al eliminar un macro:")
    print("      - Las fuentes se posicionan en Az=0°, El=0°, Dist=2m")
    print("      - Las fuentes se mutean")
    print("      - Los nombres vuelven a 'Default n'")
    print("   ✅ Estado por defecto de fuentes: MUTEADAS")
    print("   ✅ Al crear un macro: las fuentes se DESMUTEAN automáticamente")
    print("\n   ℹ️  Nota: No se encontró soporte OSC para crear grupos en SPAT")
    print("       Las fuentes se seleccionan temporalmente para agruparlas visualmente")
    
    print("\n✨ Test completado")

if __name__ == "__main__":
    test_all_fixes()