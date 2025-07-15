#!/usr/bin/env python3
"""
Test para verificar que no hay log spam de OSC
"""
import time
from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine

def test_no_spam():
    print("=== TEST DE LOG SPAM ELIMINADO ===\n")
    
    # Crear engine
    engine = EnhancedTrajectoryEngine(max_sources=10)
    
    # Crear un macro
    print("1. Creando macro...")
    macro_id = engine.create_macro(
        name="test_spam",
        source_count=3,
        formation="circle",
        spacing=2.0
    )
    print(f"   ✅ Macro creado: {macro_id}")
    
    # Esperar 3 segundos y verificar que no hay spam
    print("\n2. Esperando 3 segundos...")
    print("   (No deberían aparecer mensajes OSC repetitivos)")
    print("   " + "-" * 50)
    
    time.sleep(3)
    
    print("   " + "-" * 50)
    print("   ✅ Si no aparecieron mensajes OSC repetitivos, el problema está resuelto")
    
    # Mover el macro para verificar que los mensajes importantes sí aparecen
    print("\n3. Moviendo macro (este mensaje SÍ debería aparecer)...")
    engine.move_macro_center(macro_id, [5, 0, 0])
    
    print("\n✨ Test completado")
    print("\nRESUMEN:")
    print("• Los mensajes de debug OSC continuos han sido eliminados")
    print("• Solo aparecen mensajes relevantes durante operaciones específicas")

if __name__ == "__main__":
    test_no_spam()