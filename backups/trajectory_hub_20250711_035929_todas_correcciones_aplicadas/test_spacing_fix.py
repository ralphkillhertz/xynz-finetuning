#!/usr/bin/env python3
"""
Prueba de corrección de ajuste de spacing
"""
import numpy as np
from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine

def test_spacing_with_name_lookup():
    """Probar ajuste de spacing usando nombre del macro"""
    
    print("=== PRUEBA DE AJUSTE DE SPACING CON BÚSQUEDA POR NOMBRE ===\n")
    
    engine = EnhancedTrajectoryEngine(max_sources=100)
    
    # Crear un macro
    print("1. Creando macro 'test_grid' con formación grid...")
    macro_id = engine.create_macro(
        name="test_grid",
        source_count=9,
        formation="grid",
        spacing=1.0
    )
    
    print(f"   Macro creado: {macro_id}")
    
    # Probar select_macro con nombre
    print("\n2. Buscando macro por nombre 'test_grid'...")
    macro_info = engine.select_macro("test_grid")
    if macro_info:
        print(f"   ✅ Encontrado:")
        print(f"      Key: {macro_info['key']}")
        print(f"      Name: {macro_info['name']}")
        print(f"      Formation: {macro_info['formation']}")
        print(f"      Spacing: {macro_info['spacing']}")
    else:
        print("   ❌ No encontrado")
        return
    
    # Ajustar spacing usando el key completo
    print("\n3. Ajustando spacing usando key completo...")
    success = engine.adjust_macro_spacing(macro_info['key'], 3.0)
    if success:
        print("   ✅ Spacing ajustado exitosamente")
    else:
        print("   ❌ Error al ajustar spacing")
    
    # Verificar el cambio
    print("\n4. Verificando el cambio...")
    macro_info_updated = engine.select_macro("test_grid")
    if macro_info_updated:
        print(f"   Nuevo spacing: {macro_info_updated['spacing']}")
    
    print("\n✨ Prueba completada")

if __name__ == "__main__":
    test_spacing_with_name_lookup()