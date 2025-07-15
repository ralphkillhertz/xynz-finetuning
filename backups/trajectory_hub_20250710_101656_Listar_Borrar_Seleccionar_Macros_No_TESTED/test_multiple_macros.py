#!/usr/bin/env python3
"""
🧪 Test: Crear múltiples macros
"""

from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
from trajectory_hub.core.spat_osc_bridge import SpatOSCBridge
import time

def test_macros():
    print("🧪 TEST MÚLTIPLES MACROS")
    print("=" * 50)
    
    # Inicializar
    osc = SpatOSCBridge(host="127.0.0.1", port=9000)
    engine = EnhancedTrajectoryEngine(osc_bridge=osc)
    engine.start()
    
    print("\n🎯 Creando 5 macros...")
    
    macros = []
    formations = ["circle", "line", "grid", "spiral", "sphere"]
    
    for i, formation in enumerate(formations):
        print(f"\n{i+1}. Creando macro '{formation}' con 8 sources...")
        try:
            macro_id = engine.create_macro(
                name=f"macro_{formation}",
                source_count=8,
                formation=formation,
                spacing=3.0
            )
            macros.append(macro_id)
            print(f"   ✅ Macro creado: {macro_id}")
            
            # Verificar sources activas
            active = len(engine._active_sources)
            print(f"   📊 Total sources activas: {active}")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n📊 RESUMEN:")
    print(f"   Macros creados: {len(macros)}")
    print(f"   Sources totales: {len(engine._active_sources)}")
    print(f"   IDs de macros: {macros}")
    
    # Esperar un poco
    print("\n⏱️ Esperando 5 segundos...")
    time.sleep(5)
    
    engine.stop()
    print("\n✅ Test completado")

if __name__ == "__main__":
    test_macros()