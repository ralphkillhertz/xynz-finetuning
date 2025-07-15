#!/usr/bin/env python3
"""
Test de las correcciones para SPAT
Verifica que los índices empiecen desde 0 y los nombres se restauren
"""
import time
import numpy as np
from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine

def test_spat_fixes():
    print("=== TEST DE CORRECCIONES SPAT ===\n")
    
    # Crear engine
    engine = EnhancedTrajectoryEngine(max_sources=100)
    
    # 1. Crear un macro con pocas fuentes para verificar índices
    print("1. Creando macro 'test_indices' con 4 fuentes...")
    macro_id = engine.create_macro(
        name="test_indices",
        source_count=4,
        formation="line",
        spacing=2.0
    )
    print(f"   ✅ Macro creado: {macro_id}")
    print("   📝 Verificar en SPAT:")
    print("      - Fuente 1: test_indices_1")
    print("      - Fuente 2: test_indices_2")
    print("      - Fuente 3: test_indices_3")
    print("      - Fuente 4: test_indices_4")
    
    time.sleep(3)
    
    # 2. Desactivar el macro para verificar que todas las fuentes se muteen
    print("\n2. Desactivando el macro (verificar que TODAS las fuentes se muteen)...")
    engine.enable_macro(macro_id, False)
    print("   ⏸️ Macro desactivado - verificar que fuentes 1-4 estén muteadas Y desactivadas")
    
    time.sleep(3)
    
    # 3. Reactivar el macro
    print("\n3. Reactivando el macro...")
    engine.enable_macro(macro_id, True)
    print("   ▶️ Macro reactivado - fuentes 1-4 deberían estar activas y con audio")
    
    time.sleep(2)
    
    # 4. Crear segundo macro para tener múltiples
    print("\n4. Creando segundo macro 'otro_test' con 3 fuentes...")
    macro_id2 = engine.create_macro(
        name="otro_test",
        source_count=3,
        formation="circle",
        spacing=3.0
    )
    print(f"   ✅ Segundo macro creado: {macro_id2}")
    print("   📝 Verificar nombres:")
    print("      - Fuente 5: otro_test_1")
    print("      - Fuente 6: otro_test_2")
    print("      - Fuente 7: otro_test_3")
    
    time.sleep(3)
    
    # 5. Eliminar el primer macro y verificar restauración de nombres
    print("\n5. Eliminando primer macro 'test_indices'...")
    engine.delete_macro(macro_id)
    print("   🗑️ Macro eliminado")
    print("   📝 Verificar que los nombres volvieron a:")
    print("      - Fuente 1: Default 1")
    print("      - Fuente 2: Default 2")
    print("      - Fuente 3: Default 3")
    print("      - Fuente 4: Default 4")
    
    time.sleep(3)
    
    # 6. Verificar que el segundo macro sigue intacto
    print("\n6. El segundo macro 'otro_test' debería seguir con sus nombres:")
    print("      - Fuente 5: otro_test_1")
    print("      - Fuente 6: otro_test_2")
    print("      - Fuente 7: otro_test_3")
    
    # 7. Listar macros activos
    print("\n7. Macros activos:")
    macros = engine.list_macros()
    for macro in macros:
        print(f"   • {macro['name']}: {macro['num_sources']} fuentes")
    
    print("\n✨ Test completado")
    print("\nPUNTOS CLAVE A VERIFICAR:")
    print("1. Los nombres empiezan desde la fuente 1 (no desde la 2)")
    print("2. Al desactivar, TODAS las fuentes se mutean (incluyendo la primera)")
    print("3. Al eliminar un macro, los nombres vuelven a 'Default n'")
    print("4. Los otros macros mantienen sus nombres personalizados")

if __name__ == "__main__":
    test_spat_fixes()