#!/usr/bin/env python3
"""
Debug del error en bucle al crear macro
"""
from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine

def test_create_debug():
    print("=== DEBUG CREATE MACRO ===\n")
    
    # Crear engine
    print("1. Creando engine...")
    engine = EnhancedTrajectoryEngine(max_sources=10)
    print("   ✅ Engine creado\n")
    
    # Crear un macro pequeño
    print("2. Creando macro con 3 fuentes...")
    try:
        macro_id = engine.create_macro(
            name="debug",
            source_count=3,
            formation="line",
            spacing=2.0
        )
        print(f"   ✅ Macro creado: {macro_id}\n")
        
        # Verificar que el macro existe
        print("3. Verificando macro...")
        macro_info = engine.select_macro(macro_id)
        if macro_info:
            print(f"   ✅ Macro encontrado: {macro_info['name']}")
            print(f"   • Fuentes: {macro_info['source_ids']}")
            print(f"   • Cantidad: {macro_info['num_sources']}")
        else:
            print("   ❌ Macro no encontrado")
            
    except Exception as e:
        print(f"   ❌ Error al crear macro: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n✨ Debug completado")

if __name__ == "__main__":
    test_create_debug()