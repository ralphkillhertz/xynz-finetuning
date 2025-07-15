#!/usr/bin/env python3
# 🧪 Test: Verificar que TODAS las 30 sources lleguen a Spat
# ⚡ Mismo test que antes, ahora debería funcionar

import time
from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
from trajectory_hub.core.spat_osc_bridge import SpatOSCBridge

def test_30_sources():
    print("\n🧪 TEST 30 SOURCES DESPUÉS DEL FIX")
    print("=" * 60)
    
    # Crear engine y OSC
    engine = EnhancedTrajectoryEngine()
    engine.osc_bridge = SpatOSCBridge()
    
    # Verificar nuevo límite
    print(f"✅ n_sources en OSC Bridge: {engine.osc_bridge.n_sources}")
    print("✅ Sistema inicializado")
    
    # Iniciar engine
    engine.start()
    print("✅ Engine iniciado\n")
    
    # Crear 3 macros de 10 sources = 30 total
    print("🎯 Creando 30 sources en total...")
    
    # Macro 1: Circle
    engine.create_macro("circle_test", 10, formation="circle", spacing=3.0)
    print("   ✅ Macro 1: 10 sources (circle)")
    
    # Macro 2: Line  
    engine.create_macro("line_test", 10, formation="line", spacing=2.0)
    print("   ✅ Macro 2: 10 sources (line)")
    
    # Macro 3: Grid
    engine.create_macro("grid_test", 10, formation="grid", spacing=2.5)
    print("   ✅ Macro 3: 10 sources (grid)")
    
    print(f"\n📊 Total sources creadas: {len(engine._active_sources)}")
    print("📡 Enviando a Spat...")
    print("\n⏰ Esperando 5 segundos para verificar en Spat...")
    
    for i in range(5):
        time.sleep(1)
        print(f"   {5-i}...")
    
    # Detener
    engine.stop()
    print("\n✅ Test completado")
    print("\n🎯 VERIFICA EN SPAT:")
    print("   - Deberías ver sources 1-30")
    print("   - NO solo 1-15 como antes")
    print("   - Si funciona, el límite está resuelto! 🎉")

if __name__ == "__main__":
    test_30_sources()